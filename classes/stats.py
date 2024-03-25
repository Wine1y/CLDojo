from abc import ABC, abstractmethod

from utils.style import OutputStyler


class UserStats(ABC):

    @abstractmethod
    def styled_str(self, styler: OutputStyler) -> str:
        ...