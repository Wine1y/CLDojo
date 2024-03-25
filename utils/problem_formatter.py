import re
from typing import Dict, Optional

from classes.persistent_problem import PersistentProblem
from classes.language import Language
from classes.exceptions import InvalidProblemText


PROBLEM_PATTERN = r"(?P<cmnt>\S+) (?P<title>.*) \((?P<dif>.*)\)\n+\1 Category: (?P<cat>.*)(?:\n+\1 Tags: (?P<tags>.*))?\n+(?P<meta>(?:\1.*\n)*)\n+(?P<desc>(?:\1.*\n)*)(?P<code>[\s\S]*)"

class ProblemFormatter():
    problem_re: re.Pattern
    max_description_line_length: int
    code_prefixes: Dict[str, Optional[str]]

    def __init__(
        self,
        max_description_line_length: int,
        code_prefixes: Optional[Dict[str, Optional[str]]]=None
    ) -> None:
        self.problem_re = re.compile(PROBLEM_PATTERN)
        self.max_description_line_length = max_description_line_length
        self.code_prefixes = code_prefixes or dict()

    def get_problem_text(self, problem: PersistentProblem) -> str:
        cmnt = problem.language.comment_symbol
        metadata = "\n".join((f"{cmnt} {key}={self._disable_newlines(value)}" for key, value in problem.metadata.items() if value is not None))
        description = self._format_description(problem.description, cmnt)
        header = f"{cmnt} {problem.title} ({problem.difficulty})\n{cmnt} Category: {problem.category}"
        
        if len(problem.tags) > 0:
            header+=f"\n{cmnt} Tags: {', '.join(problem.tags)}"
        
        if (code_prefix := self.code_prefixes.get(problem.language.name)) is not None:
            solution_code = f"{code_prefix}{problem.solution_code}"
        else:
            solution_code = problem.solution_code
        
        return f"{header}\n\n{metadata}\n\n\n{description}\n\n\n{solution_code}"
    
    def parse_problem(
        self,
        problem_slug: str,
        language: Language,
        problem_text: str
    ) -> PersistentProblem:
        match = self.problem_re.match(problem_text)
        if match is None:
            raise InvalidProblemText(f"Problem \"{problem_slug}\" is invalid")
            
        cmnt = match.group("cmnt")
        metadata_lines = match.group("meta").replace(f"{cmnt} ", "").strip("\n").split("\n")
        metadata = {
            line[:delimeter]: self._enable_newlines(line[delimeter+1:])
            for line in metadata_lines
            if (delimeter := line.find("="))
            }

        return PersistentProblem(
            title=match.group("title"),
            title_slug=problem_slug,
            difficulty=match.group("dif"),
            category=match.group("cat"),
            tags=tags.split(", ") if (tags := match.group("tags")) is not None else list(),
            description=match.group("desc").replace(f"{cmnt} ", "").strip("\n"),
            language=language,
            solution_code=match.group("code").strip("\n"),
            metadata=metadata
        )
    
    def _disable_newlines(self, text: str) -> str:
        return text.replace("\n", r"\n")
    
    def _enable_newlines(self, text: str) -> str:
        return text.replace(r"\n", "\n")
    
    def _format_description(self, description: str, cmnt: str) -> str:
        if self.max_description_line_length <= 0:
            return f"{cmnt} "+description.replace('\r', '').replace("\n", f"\n{cmnt} ")

        description_lines = description.replace('\r', '').splitlines()
        for i in range(len(description_lines)):
            if len(description_lines[i]) > self.max_description_line_length:
                description_lines[i] = self._wrap_line(description_lines[i])

        return f"{cmnt} "+'\n'.join(description_lines).replace("\n", f"\n{cmnt} ")

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
            
        return '\n '.join(lines)