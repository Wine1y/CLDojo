from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict
from pathlib import Path

from utils.problem_keeper import ProblemKeeper
from .language import Language
from .persistent_problem import PersistentProblem


@dataclass()
class Problem(ABC):
    title: str
    title_slug: str
    difficulty: str
    category: str
    tags: List[str]
    description: str
    language: Language
    solution_code: str
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, str]:
        ...
    
    def save(self, keeper: ProblemKeeper, include_tags: bool=True) -> Path:
        return keeper.save_problem(PersistentProblem(
            title=self.title,
            title_slug=self.title_slug,
            difficulty=self.difficulty,
            category=self.category,
            tags=self.tags if include_tags else list(),
            description=self.description,
            language=self.language,
            solution_code=self.solution_code,
            metadata=self.get_metadata()
        ))
    
    @classmethod
    def load(cls, title_slug: str, language: Language, keeper: ProblemKeeper) -> "Problem":
        data = keeper.load_problem(title_slug, language)
        return cls(
            title=data.title,
            title_slug=data.title_slug,
            difficulty=data.difficulty,
            category=data.category,
            tags=data.tags,
            description=data.description,
            language=data.language,
            solution_code=data.solution_code,
            **data.metadata
        )