from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
from utils.style import OutputStyler

from classes.language import Language


@dataclass()
class ResultState:
    symbol: str
    symbol_color: str
    value: str

    def __str__(self) -> str:
        return f"[{self.symbol}]{self.value}"
    
    def styled_str(self, styler: OutputStyler) -> str:
        return f"[{styler.style_with_color(self.symbol, self.symbol_color)}]{self.value}"

class ResultStates(Enum):
    Accepted = ResultState('✔', 'bright_green', "Accepted")
    Rejected = ResultState('✘', 'bright_red', "Rejected")
    Error = ResultState('!', 'red', "Error")
    Unknown = ResultState('?', 'bright_blue', "Something went wrong")


@dataclass()
class CommitResult(ABC):
    problem_title: str
    language: Language
    state: ResultState
    
    @abstractmethod
    def cut_lines(self, max_line_length: int) -> None:
        ...

    @abstractmethod
    def __str__(self) -> str:
        ...
        
    @abstractmethod
    def styled_str(self, _: OutputStyler) -> str:
        ...
    
