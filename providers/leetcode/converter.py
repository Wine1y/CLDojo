from typing import Dict, Any, Optional

from bs4 import BeautifulSoup

import providers.leetcode.classes as classes
import providers.leetcode.exceptions as exceptions
from classes.result import CommitResult, ResultState


class LeetCodeConverter():
    def json_to_problem(self, json: Dict[str, Any]) -> classes.LeetCodeProblem:
        premium_problem = json.get("isPaidOnly") or json.get("paidOnly") or False

        if premium_problem and (json.get("content") is None or json.get("codeSnippets") is None):
            raise exceptions.PremiumRequired(f"Can't access a premium problem \"{json.get('title')}\"")

        code_snippet = None
        for snippet in json.get("codeSnippets"):
            if snippet.get("langSlug") == "python3":
                code_snippet = snippet.get("code")
            
        if code_snippet is None:
            raise NotImplementedError("This problem can't be solved in Python3 and other languages are not supported yet")

        return classes.LeetCodeProblem(
            title=json.get("title"),
            title_slug=json.get("titleSlug"),
            difficulty=json.get("difficulty"),
            category=json.get("categoryTitle"),
            tags=[tag.get("name") for tag in json.get("topicTags")],
            description=self._content_to_description(json.get("content")),
            solution_code=code_snippet,
            problem_id=json.get("questionId"),
            test_input=json.get("sampleTestCase"),
            judge_type=json.get("judgeType")
        )
    
    def json_to_commit_result(
        self,
        problem: classes.LeetCodeProblem,
        json: Dict[str, Any],
        input_data: Optional[str]=None
    ) -> CommitResult:
        match json.get("task_name"):
            case "judger.runcodetask.RunCode":
                return self._json_to_test_result(problem, json, input_data)
            case "judger.judgetask.Judge":
                return self._json_to_submit_result(problem, json)
    
    def json_to_current_username(self, json: Dict[str, Any]) -> str:
        user_status = json.get("userStatus")
        if user_status is None or not user_status.get("isSignedIn"):
            raise exceptions.AuthenticationFailed("Can't get current user data, check LEETCODE_SESSION cookie.")
        return user_status.get("username")
    
    def json_to_user_stats(
        self,
        username: str,
        profile_json: Dict[str, Any],
        languages_json: Dict[str, Any],
        problems_json: Dict[str, Any]
    ) -> classes.LeetCodeUserStats:
        if profile_json.get("matchedUser") is None:
            raise exceptions.UserNotFound(f"User {username} was not found")

        profile = profile_json.get("matchedUser").get("profile")
        total_problems = {
            classes.LeetCodeProblemDifficulty.from_str(counter.get("difficulty")): counter.get("count")
            for counter in problems_json.get("allQuestionsCount")
        }

        solved_problems = {
            classes.LeetCodeProblemDifficulty.from_str(counter.get("difficulty")): counter.get("count")
            for counter in problems_json.get("matchedUser").get("submitStatsGlobal").get("acSubmissionNum")
        }

        beats_percentage = {
            classes.LeetCodeProblemDifficulty.from_str(counter.get("difficulty")): counter.get("percentage")
            for counter in problems_json.get("matchedUser").get("problemsSolvedBeatsStats")
        }

        return classes.LeetCodeUserStats(
            username=username,
            real_name=real_name if len((real_name := profile.get("realName"))) > 0 else None,
            rank=profile.get("ranking"),
            views_count=profile.get("postViewCount"),
            solution_count=profile.get("solutionCount"),
            discuss_count=profile.get("categoryDiscussCount"),
            reputation=profile.get("reputation"),
            languages_problems_sovled={
                language.get("languageName"): language.get("problemsSolved")
                for language in languages_json.get("matchedUser").get("languageProblemCount")
            },
            difficulty_problems_stats={
                difficulty: classes.DifficultyProblemsStats(
                    total_problems=total_problems.get(difficulty),
                    solved=solved_problems.get(difficulty),
                    beats_percentage=beats_percentage.get(difficulty)
                )
                for difficulty in classes.LeetCodeProblemDifficulty
            }
        )
    
    def _json_to_test_result(
        self,
        problem: classes.LeetCodeProblem,
        json: Dict[str, Any],
        input_data: Optional[str]=None
        ) -> CommitResult:
        is_error = json.get("runtime_error") is not None
        is_time_limit_exceeded = json.get("status_msg") == "Time Limit Exceeded"

        match json.get("state"):
            case "SUCCESS" if (correct := json.get("correct_answer")) is not None and correct:
                state = ResultState.Accepted
            case "SUCCESS" if is_error or is_time_limit_exceeded:
                state = ResultState.Error
            case "SUCCESS":
                state = ResultState.Rejected
            case _:
                state = ResultState.Unknown
            
        answer = "\n".join(answer_list) if (answer_list := json.get("code_answer")) is not None else None
        exp_answer = "\n".join(exp_answer_list) if (exp_answer_list := json.get("expected_code_answer")) is not None else None
        output = "\n".join(out_list) if (out_list := json.get("code_output")) is not None else None

        error = json.get("runtime_error")
        if is_time_limit_exceeded:
            error = "Time Limit Exceeded"
            if (elapsed_time := json.get("elapsed_time")) is not None:
                error += f" ({round(elapsed_time/1000,2 )}s)"

        return classes.LeetCodeCommitResult(
            problem_title=f"{problem.title}(Test)",
            state=state,
            memory=json.get("status_memory"),
            runtime=json.get("status_runtime"),
            memory_percentile=json.get("memory_percentile"),
            runtime_percentile=json.get("runtime_percentile"),
            answer=answer,
            expected_answer=exp_answer,
            input=input_data,
            output=output,
            error=error
        )
    
    def _json_to_submit_result(
        self,
        problem: classes.LeetCodeProblem,
        json: Dict[str, Any]
    ) -> CommitResult:
        is_error = json.get("runtime_error") is not None
        is_time_limit_exceeded = json.get("status_msg") == "Time Limit Exceeded"

        match json.get("state"):
            case "SUCCESS" if json.get("total_correct") == json.get("total_testcases"):
                state = ResultState.Accepted
            case "SUCCESS" if is_error or is_time_limit_exceeded:
                state = ResultState.Error
            case "SUCCESS":
                state = ResultState.Rejected
            case _:
                state = ResultState.Unknown

        error = json.get("runtime_error")
        if is_time_limit_exceeded:
            error = "Time Limit Exceeded"
            if (elapsed_time := json.get("elapsed_time")) is not None:
                error += f" ({round(elapsed_time/1000,2 )}s)"

        return classes.LeetCodeCommitResult(
            problem_title=problem.title,
            state=state,
            memory=json.get("status_memory"),
            runtime=json.get("status_runtime"),
            memory_percentile=json.get("memory_percentile"),
            runtime_percentile=json.get("runtime_percentile"),
            answer=json.get("code_output"),
            expected_answer=json.get("expected_output"),
            input=json.get("last_testcase"),
            output=json.get("std_output"),
            error=error
        )

    def _content_to_description(self, problem_content: str) -> str:
        soup = BeautifulSoup(f"<html>{problem_content}</html", features="lxml")
        for img in soup.select("img"):
            img.name = "span"
            img.append(img.attrs.get("src"))
        return soup.text
