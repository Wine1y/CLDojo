from typing import Dict, Optional
from enum import Enum
from dataclasses import dataclass, field

from utils.style import OutputStyler, ColorType
from classes.problem import Problem
from classes.result import CommitResult
from classes.stats import UserStats


@dataclass()
class LeetCodeProblem(Problem):
    problem_id: str
    test_input: str
    judge_type: str
    study_plan_slug: Optional[str] = field(default=None)
    
    def get_metadata(self) -> Dict[str, str]:
        return {
            "problem_id": self.problem_id,
            "test_input": self.test_input,
            "judge_type": self.judge_type,
            "study_plan_slug": self.study_plan_slug
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
    
    
    def cut_lines(self, max_line_length: int) -> None:
        for line in ["input", "answer", "expected_answer", "output", "error"]:
            line_value = getattr(self, line)
            if line_value is not None and len(line_value) > max_line_length:
                setattr(self, line, f"{line_value[:max_line_length]}... ({len(line_value)-max_line_length} characters more)")
    
    def __str__(self) -> str:
        memory, runtime = self.memory or "", self.runtime or ""
        if self.memory_percentile is not None:
            memory+=f"({round(self.memory_percentile, 2)}%)"
        if self.runtime_percentile is not None:
            runtime+=f"({round(self.runtime_percentile, 2)}%)"

        lines = [
            ("Input", self.input), ("Output", self.answer),
            ("Expected", self.expected_answer), ("StdOut", self.output), ("Error", self.error)
        ]
        body = '\n\n'.join([
            f"{line[0]}:\n{line[1]}"
            for line in lines
            if line[1] is not None and len(line[1]) > 0
        ])

        result_str = f"{self.problem_title} ({self.language.name}): {self.state}\nMemory: {memory}, Runtime: {runtime}"

        if len(body) > 0:
            result_str+=f"\n\n{body}"

        return result_str
    
    def styled_str(self, styler: OutputStyler) -> str:
        dlmt = styler.style(':', ColorType.DELIMITER)

        memory, runtime = self.memory or "", self.runtime or ""
        memory, runtime = styler.style(memory, ColorType.VALUE), styler.style(runtime, ColorType.VALUE)
        if self.memory_percentile is not None:
            memory+=f"({round(self.memory_percentile, 2)}%)"
        if self.runtime_percentile is not None:
            runtime+=f"({round(self.runtime_percentile, 2)}%)"

        lines = [
            ("Input", self.input), ("Output", self.answer),
            ("Expected", self.expected_answer), ("StdOut", self.output), ("Error", self.error)
        ]
        body = '\n\n'.join([
            f"{line[0]}{dlmt}\n{line[1]}"
            for line in lines
            if line[1] is not None and len(line[1]) > 0
        ])

        title = styler.style(self.problem_title, ColorType.TITLE)
        language = styler.style(self.language.name, ColorType.LANGUAGE)
        result_str = f"{title} ({language}){dlmt} {self.state.styled_str(styler)}\nMemory{dlmt} {memory}, Runtime{dlmt} {runtime}"

        if len(body) > 0:
            result_str+=f"\n\n{body}"

        return result_str

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
class LeetCodeUserStats(UserStats):
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

    def styled_str(self, styler: OutputStyler) -> str:
        dlmt = styler.style(':', ColorType.DELIMITER)
        username = f"{self.username} ({self.real_name})" if self.real_name is not None else self.username
        username = styler.style(username, ColorType.TITLE)
        
        metrics = [
            ("Rank", self.rank), ("Views", self.views_count),
            ("Solution", self.solution_count), ("Discuss", self.discuss_count),
            ("Reputation", self.reputation)
        ]

        metrics = '\n'.join(f"{metric[0]}{dlmt} {styler.style(metric[1], ColorType.VALUE)}" for metric in metrics)
        languages = '\n'.join((
            f"{language}{dlmt} {styler.style(count, ColorType.VALUE)} problems sovled"
            for language, count in self.languages_problems_sovled.items()
        ))
        problems = '\n'.join((
            f"{difficulty.value.capitalize()}{dlmt} {stats.styled_str(styler)}"
            for difficulty, stats in self.difficulty_problems_stats.items()
        ))

        return f"{username}\n\n{metrics}\n\nLanguages:\n{languages}\n\nProblems solved:\n{problems}"

@dataclass()
class DifficultyProblemsStats:
    total_problems: int
    solved: int
    beats_percentage: Optional[float]

    def __str__(self) -> str:
        string = f"{self.solved}/{self.total_problems}"
        if self.beats_percentage is not None:
            string+=f" (Beats {round(self.beats_percentage, 2)}%)"
        return string
    
    def styled_str(self, styler: OutputStyler) -> str:
        string = styler.style(f"{self.solved}/{self.total_problems}", ColorType.VALUE)
        if self.beats_percentage is not None:
            string+=f" (Beats {round(self.beats_percentage, 2)}%)"
        return string