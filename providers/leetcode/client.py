from typing import Dict, Any, Optional
from time import sleep
from pathlib import Path
from http.cookiejar import MozillaCookieJar

import requests

import providers.leetcode.classes as classes
from classes.result import CommitResult
from .converter import LeetCodeConverter


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}
PENDING_DELAY_S = 2

class LeetCodeClient:
    BASE_URL = "https://leetcode.com/"
    session: requests.Session
    converter: "LeetCodeConverter"

    def __init__(self, cookies_file_path: Path) -> None:
        self.session = requests.Session()
        self.converter = LeetCodeConverter()
        self.session.headers = HEADERS

        jar = MozillaCookieJar(cookies_file_path)
        jar.load(cookies_file_path, ignore_expires=True)

        self.session.cookies.update(jar)

        if (csrf_token := self.session.cookies.get("csrftoken")) is not None:
            self.session.headers["X-Csrftoken"] = csrf_token
        else:
            raise RuntimeError("No csrf cookie provided")
        
        if self.session.cookies.get("LEETCODE_SESSION") is None:
            raise RuntimeError("No LEETCODE_SESSION cookie provided")
        

    def get_problem(self, title_slug: str) -> classes.LeetCodeProblem:
        resp = self._make_graphql_request(
            "questionData",
            "query questionData($titleSlug: String!) {\n  question(titleSlug: $titleSlug) {\n    questionId\n    isPaidOnly\n    title\n    titleSlug\n    content\n    difficulty\n    categoryTitle\n    topicTags {\n      name\n    }\n    codeSnippets {\n      langSlug\n      code\n    }\n    sampleTestCase\n    judgeType\n  }\n}\n",
            titleSlug=title_slug
        )

        return self.converter.json_to_problem(resp.json().get("data").get("question"))
    
    def test_solution(self, problem: classes.LeetCodeProblem, test_input: Optional[str]) -> CommitResult:
        test_input = test_input or problem.test_input
        resp = self._make_request(
            f"problems/{problem.title_slug}/interpret_solution/",
            "POST",
            headers={
                "Referer": f"https://leetcode.com/problems/{problem.title_slug}/"
            },
            json={
                "question_id": problem.problem_id,
                "data_input": test_input,
                "lang": "python3",
                "typed_code": problem.solution_code,
                "judge_type": problem.judge_type
            }
        )

        run_id = resp.json().get("interpret_id")
        result = self._await_running_submission(problem, run_id, test_input)
        return result
    
    def submit_solution(self, problem: classes.LeetCodeProblem) -> CommitResult:
        resp = self._make_request(
            f"problems/{problem.title_slug}/submit/",
            "POST",
            headers={
                "Referer": f"https://leetcode.com/problems/{problem.title_slug}/"
            },
            json={
                "question_id": problem.problem_id,
                "lang": "python3",
                "typed_code": problem.solution_code,
            }
        )

        run_id = resp.json().get("submission_id")
        return self._await_running_submission(problem, run_id)
    
    def search_problem(self, problem_title: str) -> Optional[classes.LeetCodeProblem]:
        resp = self._make_graphql_request(
            "problemsetQuestionList",
            "\n    query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {\n  problemsetQuestionList: questionList(\n    categorySlug: $categorySlug\n    limit: $limit\n    skip: $skip\n    filters: $filters\n  ) {\n    total: totalNum\n    questions: data {\n    questionId\n    isPaidOnly\n    title\n    titleSlug\n    content\n    difficulty\n    categoryTitle\n    topicTags {\n      name\n    }\n    codeSnippets {\n      langSlug\n      code\n    }\n    sampleTestCase\n    judgeType\n  }\n  }\n}\n    ",
            categorySlug="all-code-essentials",
            skip=0,
            limit=1,
            filters={"searchKeywords": problem_title.lower()}
        )
        
        problems = resp.json().get("data").get("problemsetQuestionList").get("questions")
        if len(problems) == 0:
            return None
        
        return self.converter.json_to_problem(problems[0])
    
    def get_random_problem(
        self,
        difficulty: Optional[classes.LeetCodeProblemDifficulty]=None,
        include_solved: bool=False
    ) -> classes.LeetCodeProblem:
        filters = {}
        if difficulty is not None:
            filters["difficulty"] = difficulty.value.upper()
        if not include_solved:
            filters["status"] = "NOT_STARTED"

        resp = self._make_graphql_request(
            "randomQuestion",
            "\n    query randomQuestion($categorySlug: String, $filters: QuestionListFilterInput) {\n  randomQuestion(categorySlug: $categorySlug, filters: $filters) {\n    questionId\n    isPaidOnly\n    title\n    titleSlug\n    content\n    difficulty\n    categoryTitle\n    topicTags {\n      name\n    }\n    codeSnippets {\n      langSlug\n      code\n    }\n    sampleTestCase\n    judgeType\n  }\n}\n    ",
            categorySlug="all-code-essentials",
            filters=filters
        )

        return self.converter.json_to_problem(resp.json().get("data").get("randomQuestion"))
    
    def get_problem_of_today(self) -> classes.LeetCodeProblem:
        resp = self._make_graphql_request(
            "questionOfToday",
            "\n    query questionOfToday {\n  activeDailyCodingChallengeQuestion {\n    question {\n    questionId\n    isPaidOnly\n    title\n    titleSlug\n    content\n    difficulty\n    categoryTitle\n    topicTags {\n      name\n    }\n    codeSnippets {\n      langSlug\n      code\n    }\n    sampleTestCase\n    judgeType\n  }\n  }\n}\n    ",
        )

        return self.converter.json_to_problem(
            resp.json().get("data").get("activeDailyCodingChallengeQuestion").get("question")
        )
    
    def get_next_plan_problem(self, plan_slug: str) -> Optional[classes.LeetCodeProblem]:
        resp = self._make_graphql_request(
            "studyPlanDetail",
            "\n    query studyPlanDetail($slug: String!) {\n  studyPlanV2Detail(planSlug: $slug) {\n    slug\n    name\n    highlight\n    staticCoverPicture\n    colorPalette\n    threeDimensionUrl\n    description\n    premiumOnly\n    needShowTags\n    awardDescription\n    defaultLanguage\n    award {\n      name\n      config {\n        icon\n        iconGif\n        iconGifBackground\n      }\n    }\n    relatedStudyPlans {\n      cover\n      highlight\n      name\n      slug\n      premiumOnly\n    }\n    planSubGroups {\n      slug\n      name\n      premiumOnly\n      questionNum\n      questions {\n        titleSlug\n      paidOnly\n      status\n      }\n    }\n  }\n}\n    ",
            slug=plan_slug
        )

        plan_data = resp.json().get("data").get("studyPlanV2Detail")
        if plan_data is None:
            return None
        problem_slugs = [
            problem.get("titleSlug")
            for subgroup in plan_data.get("planSubGroups")
            for problem in subgroup.get("questions")
            if problem.get("status") != "PAST_SOLVED"
        ]

        if len(problem_slugs) == 0:
            return None
        return self.get_problem(problem_slugs[0])

    def get_current_username(self) -> str:
        resp = self._make_graphql_request(
            "globalData",
            "\n    query globalData {\n  userStatus {\n    isSignedIn\n    username\n  }\n}\n    ",
        )
        return self.converter.json_to_current_username(resp.json().get("data"))


    def get_user_stats(self, username: str) -> Optional[classes.LeetCodeUserStats]:
        profile_resp = self._make_graphql_request(
            "userPublicProfile",
            "\n    query userPublicProfile($username: String!) {\n  matchedUser(username: $username) {\n    profile {\n      ranking\n      realName\n      postViewCount\n      reputation\n      solutionCount\n      categoryDiscussCount\n    }\n  }\n}\n    ",
            username=username
        )
        languages_resp = self._make_graphql_request(
            "languageStats",
            "\n    query languageStats($username: String!) {\n  matchedUser(username: $username) {\n    languageProblemCount {\n      languageName\n      problemsSolved\n    }\n  }\n}\n    ",
            username=username
        )
        problems_resp = self._make_graphql_request(
            "userProblemsSolved",
            "\n    query userProblemsSolved($username: String!) {\n  allQuestionsCount {\n    difficulty\n    count\n  }\n  matchedUser(username: $username) {\n    problemsSolvedBeatsStats {\n      difficulty\n      percentage\n    }\n    submitStatsGlobal {\n      acSubmissionNum {\n        difficulty\n        count\n      }\n    }\n  }\n}\n    ",
            username=username
        )
        return self.converter.json_to_user_stats(
            username,
            profile_resp.json().get("data"),
            languages_resp.json().get("data"),
            problems_resp.json().get("data")
        )

    def _await_running_submission(
        self,
        problem: classes.LeetCodeProblem,
        run_id: str,
        run_input: Optional[str]=None
    ) -> CommitResult:
        while True:
            resp = self._make_request(
                f"submissions/detail/{run_id}/check/",
                headers={
                    "Referer": f"https://leetcode.com/problems/{problem.title_slug}/"
                }
            )

            data = resp.json()
            if data.get("state") in ["PENDING", "STARTED"]:
                sleep(PENDING_DELAY_S)
                continue
            
            return self.converter.json_to_commit_result(problem, data, run_input)
    
    def _make_request(
        self,
        path: str,
        method: str="GET",
        headers: Optional[Dict[str, str]]=None,
        json: Optional[Dict[str, Any]]=None
    ) -> requests.Response:
        response = self.session.request(
            method=method,
            url=f"{self.BASE_URL}{path}",
            headers=headers,
            json=json,
            cookies=self.session.cookies.get_dict()
        )

        if response.status_code != 200:
            raise RuntimeError(f"Leetcode returned {response.status_code}" )
        return response
    
    def _make_graphql_request(
        self,
        operation_name: str,
        query: str,
        headers: Optional[Dict[str, str]]=None,
        **variables: Any,
    ):
        return self._make_request(
            path="graphql",
            method="POST",
            headers=headers,
            json={
                "operationName": operation_name,
                "variables": variables,
                "query": query
            }
        )