from typing import List
from enum import Enum
from dataclasses import dataclass


class ResultState(Enum):
    Accepted = "[✔]Accepted"
    Rejected = "[✘]Rejected"
    Error = "[!]Error"
    Unknown = "[?]Something went wrong..."

    def __str__(self) -> str:
        return self.value

@dataclass()
class CommitResult():
    problem_title: str
    state: ResultState
    
    def header_lines(self) -> List[str]:
        return list()
    
    def body_lines(self) -> List[str]:
        return list()
    
    def footer_lines(self) -> List[str]:
        return list()
    
    def __str__(self) -> str:
        header, body, footer = self.header_lines(), self.body_lines(), self.footer_lines()
        result_str = f"{self.problem_title}: {self.state}"

        if len(header) > 0:
            result_str+="\n{0}".format('\n'.join(header))
        if len(body) > 0:
            result_str+="\n\n{0}".format('\n\n'.join(body))
        if len(footer) > 0:
            result_str+="\n\n{0}".format('\n'.join(footer))

        return result_str
