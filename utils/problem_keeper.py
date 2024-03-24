import os
import platform
import subprocess
import re
from typing import Optional, Dict, Tuple
from pathlib import Path

from Levenshtein import ratio as levenshtein_ratio

from classes.persistent_problem import PersistentProblem
from classes.language import Language


class ProblemKeeper:
    problem_re: re.Pattern
    provider: str
    problems_path: Path
    code_prefixes: Dict[str, Optional[str]]
    max_description_line_length: int

    def __init__(
        self,
        provider: str,
        max_description_line_length: int,
        problems_path: Path=Path("problems"),
        code_prefixes: Optional[Dict[str, Optional[str]]]=None
    ) -> None:
        self.problem_re = re.compile(r"(?P<cmnt>\S+) (?P<title>.*) \((?P<dif>.*)\)\n+\1 Category: (?P<cat>.*)(?:\n+\1 Tags: (?P<tags>.*))?\n+(?P<meta>(?:\1.*\n)*)\n+(?P<desc>(?:\1.*\n)*)(?P<code>[\s\S]*)")
        self.provider = provider
        self.max_description_line_length = max_description_line_length
        self.code_prefixes = code_prefixes or dict()

        self.problems_path =  problems_path.joinpath(self.provider)
    
    @property
    def problems_dir(self) -> Path:
        return self.problems_path

    def save_problem(self, problem: PersistentProblem) -> Path:
        problem_path = self.get_problem_path(problem.title_slug, problem.language)

        with problem_path.open("w", encoding="utf-8") as w:
            w.write(self.get_problem_text(problem))
            
        return problem_path
    
    def load_problem(self, problem_slug: str, language: Language) -> PersistentProblem:
        problem_path = self.get_problem_path(problem_slug, language)
        if not problem_path.is_file():
            raise FileNotFoundError(f"Problem {problem_slug} is not found") 
        
        with problem_path.open("r", encoding="utf-8") as f:
            problem_text = f.read()
            if (match := self.problem_re.match(problem_text)) is not None:
                return self._parse_problem_match(problem_slug, language, match)

            raise RuntimeError(f"File {problem_path.name} is invalid")
    
    def open_problem(self, problem_slug: str, language: Language):
        path = self.get_problem_path(problem_slug, language)
        match platform.system():
            case "Darwin":
                subprocess.call(('open', path.as_posix()))
            case "Windows":
                os.startfile(path)
            case _:
                subprocess.call(('xdg-open', path.as_posix()))
    
    def delete_problems(self, language: Language) -> Tuple[int, int]:
        lang_dir = self.problems_dir.joinpath(language.name)
        removed = failed = 0

        if lang_dir.is_dir():
            for path in lang_dir.iterdir():
                if not path.is_file():
                    continue
                try:
                    os.remove(path)
                    removed+=1
                except Exception:
                    failed+=1
            os.rmdir(lang_dir)
        return removed, failed 
    
    def get_problem_path(self, problem_slug: str, language: Language) -> Path:
        problems_dir = self.problems_path.joinpath(language.name)
        problems_dir.mkdir(parents=True, exist_ok=True)
        return problems_dir.joinpath(f"{problem_slug}.{language.file_extension}")
    
    def is_problem_saved(self, problem_slug: str, language: Language) -> bool:
        return self.get_problem_path(problem_slug, language).is_file()
    
    def fuzzy_search_problem(self, problem_title: str, language: Language) -> Optional[str]:
        maxRatio, bestPath = 0, None
        lang_dir = self.problems_path.joinpath(language.name)
        if lang_dir.is_dir():
            for problem_path in lang_dir.iterdir():
                if (ratio := levenshtein_ratio(problem_title, problem_path.stem)) > maxRatio:
                    maxRatio = ratio
                    bestPath = problem_path.stem
        
        return bestPath

    def get_problem_text(self, problem: PersistentProblem) -> str:
        cmnt = problem.language.comment_symbol
        metadata = "\n".join((f"{cmnt} {key}={self._disable_newlines(value)}" for key, value in problem.metadata.items() if value is not None))
        description = self._format_description(problem.description, cmnt)
        header = f"{cmnt} {problem.title} ({problem.difficulty})\n{cmnt} Category: {problem.category}"
        if len(problem.tags) > 0:
            header+=f"\n{cmnt} Tags: {', '.join(problem.tags)}"
        
        if (code_prefix := self.code_prefixes.get(problem.language.name)) is not None:
            solution_code = f"{code_prefix}{problem.solution_code}"
        else:
            solution_code = problem.solution_code
        
        return f"{header}\n\n{metadata}\n\n\n{description}\n\n\n{solution_code}"
    
    def _parse_problem_match(
        self,
        problem_slug: str,
        language: Language,
        match: re.Match[str]
    ) -> PersistentProblem:
        cmnt = language.comment_symbol
        metadata_lines = match.group("meta").replace(f"{cmnt} ", "").strip("\n").split("\n")
        metadata = {
            line[:delimeter]: self._enable_newlines(line[delimeter+1:])
            for line in metadata_lines
            if (delimeter := line.find("="))
            }

        return PersistentProblem(
            title=match.group("title"),
            title_slug=problem_slug,
            difficulty=match.group("dif"),
            category=match.group("cat"),
            tags=tags.split(", ") if (tags := match.group("tags")) is not None else list(),
            description=match.group("desc").replace(f"{cmnt} ", "").strip("\n"),
            language=language,
            solution_code=match.group("code").strip("\n"),
            metadata=metadata
        )
    
    def _disable_newlines(self, text: str) -> str:
        return text.replace("\n", r"\n")
    
    def _enable_newlines(self, text: str) -> str:
        return text.replace(r"\n", "\n")
    
    def _format_description(self, description: str, cmnt: str) -> str:
        if self.max_description_line_length <= 0:
            return f"{cmnt} "+description.replace('\r', '').replace("\n", f"\n{cmnt} ")

        description_lines = description.replace('\r', '').splitlines()
        for i in range(len(description_lines)):
            if len(description_lines[i]) > self.max_description_line_length:
                description_lines[i] = self._wrap_line(description_lines[i])

        return f"{cmnt} "+'\n'.join(description_lines).replace("\n", f"\n{cmnt} ")

    def _wrap_line(self, line: str) -> str:
        lines = [[]]
        line_length = 0

        for word in line.split():
            if line_length == 0:
                lines[-1].append(word)
                line_length=len(word)
                continue

            if line_length+1+len(word) > self.max_description_line_length:
                lines.append(list())
                line_length=len(word)
            else:
                line_length+=1+len(word)

            lines[-1].append(word)
        
        for i in range(len(lines)):
            lines[i] = ' '.join(lines[i])
            
        return '\n '.join(lines)
            