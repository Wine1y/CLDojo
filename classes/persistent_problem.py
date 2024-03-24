from typing import List, Dict
from dataclasses import dataclass

from .language import Language


@dataclass
class PersistentProblem:
    title: str
    title_slug: str
    difficulty: str
    category: str
    tags: List[str]
    description: str
    language: Language
    solution_code: str
    metadata: Dict[str, str]