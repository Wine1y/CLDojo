from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass

from classes.problem import Problem
from classes.result import CommitResult


@dataclass()
class LeetCodeProblem(Problem):
    problem_id: str
    test_input: str
    judge_type: str
    
    def get_metadata(self) -> Dict[str, str]:
        return {
            "problem_id": self.problem_id,
            "test_input": self.test_input,
            "judge_type": self.judge_type
        }

@dataclass()
class LeetCodeCommitResult(CommitResult):
    memory: Optional[str]
    runtime: Optional[str]
    memory_percentile: Optional[float]
    runtime_percentile: Optional[float]
    answer: Optional[str]
    expected_answer: Optional[str]
    input: Optional[str]
    output: Optional[str]
    error: Optional[str]

    def header_lines(self) -> List[str]:
        memory, runtime = self.memory or "", self.runtime or ""
        if self.memory_percentile is not None:
            memory+=f"({round(self.memory_percentile, 2)}%)"
        if self.runtime_percentile is not None:
            runtime+=f"({round(self.runtime_percentile, 2)}%)"
        return [
            f"Memory: {memory}, Runtime: {runtime}"
        ]
    
    def body_lines(self) -> List[str]:
        info_parts = list()
        if self.input is not None and len(self.input) > 0:
            info_parts.append(f"Input:\n{self.input}")
        if self.answer is not None and len(self.answer) > 0:
            info_parts.append(f"Output:\n{self.answer}")
        if self.expected_answer is not None and len(self.expected_answer) > 0:
            info_parts.append(f"Expected:\n{self.expected_answer}")
        if self.output is not None and len(self.output) > 0:
            info_parts.append(f"StdOut:\n{self.output}")
        if self.error is not None and len(self.error) > 0:
            info_parts.append(f"Error:\n{self.error}")
        return info_parts

class LeetCodeProblemDifficulty(Enum):
    All = "all"
    Easy = "easy"
    Medium = "medium"
    Hard = "hard"

    @classmethod
    def from_str(
        cls: "LeetCodeProblemDifficulty",
        difficulty: str
    ) -> Optional["LeetCodeProblemDifficulty"]:
        try:
            return cls(difficulty.lower())
        except ValueError:
            return None

@dataclass()
class LeetCodeUserStats:
    username: str
    real_name: Optional[str]
    rank: int
    views_count: int
    solution_count: int
    discuss_count: int
    reputation: int
    languages_problems_sovled: Dict[str, int]
    difficulty_problems_stats: Dict[LeetCodeProblemDifficulty, "DifficultyProblemsStats"]

    def __str__(self) -> str:
        username = f"{self.username} ({self.real_name})" if self.real_name is not None else self.username
        metrics = f"Rank: {self.rank}\nViews: {self.views_count}\nSolution: {self.solution_count}\nDiscuss: {self.discuss_count}\nReputation: {self.reputation}"
        languages = '\n'.join((
            f"{language}: {count} problems sovled"
            for language, count in self.languages_problems_sovled.items()
        ))
        problems = '\n'.join((
            f"{difficulty.value.capitalize()}: {stats}"
            for difficulty, stats in self.difficulty_problems_stats.items()
        ))

        return f"{username}\n\n{metrics}\n\nLanguages:\n{languages}\n\nProblems solved:\n{problems}"

@dataclass()
class DifficultyProblemsStats:
    total_problems: int
    solved: int
    beats_percentage: Optional[float]

    def __str__(self) -> str:
        if self.beats_percentage is None:
            return f"{self.solved}/{self.total_problems}"
        return f"{self.solved}/{self.total_problems} (Beats {round(self.beats_percentage, 2)}%)"