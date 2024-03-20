import os
import platform
import subprocess
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PersistentProblem:
    title: str
    title_slug: str
    difficulty: str
    category: str
    tags: List[str]
    description: str
    solution_code: str
    metadata: Dict[str, str]

class ProblemKeeper:
    problem_re: re.Pattern
    provider: str
    problems_path: Path
    code_prefix: Optional[str]=None
    max_description_line_length: int

    def __init__(
        self,
        provider: str,
        max_description_line_length: int,
        problems_path: Path=Path("problems"),
        code_prefix: Optional[str]=None
    ) -> None:
        self.problem_re = re.compile(r"# (.*) \((.*)\)\n+# Category: (.*)(?:\n+# Tags: (.*))?\n+((?:#.*\n)*)\n+((?:#.*\n)*)([\s\S]*)")
        self.provider = provider
        self.max_description_line_length = max_description_line_length
        self.code_prefix = code_prefix

        self.problems_path =  problems_path.joinpath(self.provider)
        self.problems_path.mkdir(parents=True, exist_ok=True)
    
    @property
    def problems_dir(self) -> Path:
        return self.problems_path

    def save_problem(self, problem: PersistentProblem) -> Path:
        problem_path = self.get_problem_path(problem.title_slug)

        with problem_path.open("w", encoding="utf-8") as w:
            w.write(self.get_problem_text(problem))
            
        return problem_path
    
    def load_problem(self, problem_slug: str) -> PersistentProblem:
        problem_path = self.get_problem_path(problem_slug)
        if not problem_path.is_file():
            raise FileNotFoundError(f"Problem {problem_slug} is not found") 
        
        with problem_path.open("r", encoding="utf-8") as f:
            problem_text = f.read()
            if (match := self.problem_re.match(problem_text)) is not None:
                return self._parse_problem_match(problem_slug, match)

            raise RuntimeError(f"File {problem_path.name} is invalid")
    
    def open_problem(self, problem_slug: str):
        path = self.get_problem_path(problem_slug)
        match platform.system():
            case "Darwin":
                subprocess.call(('open', path.as_posix()))
            case "Windows":
                os.startfile(path)
            case _:
                subprocess.call(('xdg-open', path.as_posix()))
    
    def get_problem_path(self, problem_slug: str) -> Path:
        return self.problems_path.joinpath(f"{problem_slug}.py")
    
    def is_problem_saved(self, problem_slug: str) -> bool:
        return self.get_problem_path(problem_slug).is_file()

    def get_problem_text(self, problem: PersistentProblem) -> str:
        metadata = "\n".join((f"# {key}={self._disable_newlines(value)}" for key, value in problem.metadata.items() if value is not None))
        description = self._format_description(problem.description)
        header = f"# {problem.title} ({problem.difficulty})\n# Category: {problem.category}"
        if len(problem.tags) > 0:
            header+=f"\n# Tags: {', '.join(problem.tags)}"
        
        if self.code_prefix is not None:
            solution_code = f"{self.code_prefix}{problem.solution_code}"
        else:
            solution_code = problem.solution_code
        
        return f"{header}\n\n{metadata}\n\n\n# {description}\n\n\n{solution_code}"
    
    def _parse_problem_match(
        self,
        problem_slug: str,
        match: re.Match[str]
    ) -> PersistentProblem:
        metadata_lines = match.group(5).replace("# ", "").strip("\n").split("\n")
        metadata = {
            line[:delimeter]: self._enable_newlines(line[delimeter+1:])
            for line in metadata_lines
            if (delimeter := line.find("="))
            }

        return PersistentProblem(
            title=match.group(1),
            title_slug=problem_slug,
            difficulty=match.group(2),
            description=match.group(6).replace("# ", "").strip("\n"),
            category=match.group(3),
            tags=tags.split(", ") if (tags := match.group(4)) is not None else list(),
            solution_code=match.group(7).strip("\n"),
            metadata=metadata
        )
    
    def _disable_newlines(self, text: str) -> str:
        return text.replace("\n", r"\n")
    
    def _enable_newlines(self, text: str) -> str:
        return text.replace(r"\n", "\n")
    
    def _format_description(self, description: str) -> str:
        if self.max_description_line_length <= 0:
            return description.replace('\r', '').replace("\n", "\n# ")

        description_lines = description.replace('\r', '').splitlines()
        for i in range(len(description_lines)):
            if len(description_lines[i]) > self.max_description_line_length:
                description_lines[i] = self._wrap_line(description_lines[i])

        return '\n'.join(description_lines).replace("\n", "\n# ")

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
            
        return '\n'.join(lines)
            