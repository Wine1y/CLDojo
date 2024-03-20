from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict
from pathlib import Path

from utils.problem_keeper import ProblemKeeper, PersistentProblem


@dataclass()
class Problem(ABC):
    title: str
    title_slug: str
    difficulty: str
    category: str
    tags: List[str]
    description: str
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
            solution_code=self.solution_code,
            metadata=self.get_metadata()
        ))
    
    @classmethod
    def load(cls, title_slug: str, keeper: ProblemKeeper) -> "Problem":
        data = keeper.load_problem(title_slug)
        return cls(
            title=data.title,
            title_slug=data.title_slug,
            difficulty=data.difficulty,
            category=data.category,
            tags=data.tags,
            description=data.description,
            solution_code=data.solution_code,
            **data.metadata
        )