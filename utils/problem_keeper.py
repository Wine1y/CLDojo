import os
import platform
import subprocess
from typing import Optional, Tuple
from pathlib import Path

from Levenshtein import ratio as levenshtein_ratio

from .problem_formatter import ProblemFormatter
from classes.persistent_problem import PersistentProblem
from classes.language import Language


class ProblemKeeper:
    provider: str
    problems_path: Path
    formatter: ProblemFormatter

    def __init__(
        self,
        provider: str,
        formatter: ProblemFormatter,
        problems_path: Path=Path("problems")
    ) -> None:
        self.provider = provider
        self.problems_path =  problems_path.joinpath(self.provider)
        self.formatter = formatter

    def save_problem(self, problem: PersistentProblem) -> Path:
        problem_path = self.get_problem_path(problem.title_slug, problem.language)
        problem_path.parent.mkdir(parents=True, exist_ok=True)

        with problem_path.open("w", encoding="utf-8") as w:
            w.write(self.formatter.get_problem_text(problem))
            
        return problem_path
    
    def load_problem(self, problem_slug: str, language: Language) -> PersistentProblem:
        problem_path = self.get_problem_path(problem_slug, language)
        if not problem_path.is_file():
            raise FileNotFoundError(f"Problem \"{problem_slug}\" was not found") 
        
        with problem_path.open("r", encoding="utf-8") as f:
            problem_text = f.read()
            return self.formatter.parse_problem(problem_slug, language, problem_text)
    
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
        lang_dir = self.language_dir(language)
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
    
    @property
    def problems_dir(self) -> Path:
        return self.problems_path
    
    def language_dir(self, language: Language) -> Path:
        return self.problems_dir.joinpath(language.name)
    
    def get_problem_path(self, problem_slug: str, language: Language) -> Path:
        problems_dir = self.language_dir(language)
        return problems_dir.joinpath(f"{problem_slug}.{language.file_extension}")
    
    def is_problem_saved(self, problem_slug: str, language: Language) -> bool:
        return self.get_problem_path(problem_slug, language).is_file()
    
    def fuzzy_search_problem(self, problem_title: str, language: Language) -> Optional[str]:
        maxRatio, bestSlug = 0, None
        lang_dir = self.problems_path.joinpath(language.name)
        if lang_dir.is_dir():
            for problem_path in lang_dir.iterdir():
                if (ratio := levenshtein_ratio(problem_title, problem_path.stem)) > maxRatio:
                    maxRatio = ratio
                    bestSlug = problem_path.stem
        
        return bestSlug