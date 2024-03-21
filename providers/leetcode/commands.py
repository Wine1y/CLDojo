import os
import re
from time import sleep
from typing import Optional, Tuple

import click
from slugify import slugify

from .client import LeetCodeClient
from .classes import LeetCodeProblemDifficulty
from providers.leetcode.classes import LeetCodeProblem
from providers.leetcode.exceptions import PremiumRequired, AuthenticationFailed
from utils.problem_keeper import ProblemKeeper
from utils.click import pass_client, pass_keeper, pass_config
from utils.config import Config


@click.command("get")
@click.argument("PROBLEM")
@click.option("--rewrite", "-r", default=False, is_flag=True,
              help="Rewrite existing problem without confirmation")
@click.option('--open/--no-open', '-o/-no', default=None,
              help="Open problem in default code editor")
@click.option('--tags/--no-tags', '-t/-nt', default=None,
              help="Show problem tags (may contain solution hints)")
@pass_config
@pass_keeper
@pass_client
def get(
    client: LeetCodeClient,
    keeper: ProblemKeeper,
    config: Config,
    problem: str,
    rewrite: bool,
    open: Optional[bool],
    tags: Optional[bool]
):
    """Download specified problem\n
    PROBLEM: problem url or title"""

    problem_url_re = re.compile("leetcode\.com\/problems\/([\w-]+)")
    if (match := problem_url_re.search(problem)) is not None:
        fetched_problem = client.get_problem(match.group(1))
    else:
        fetched_problem = client.search_problem(problem)

    if fetched_problem is None:
        click.echo(f"Problem \"{problem}\" was not found")
        return
    open_problem = open if open is not None else config.get("main", "open_saved_problems")
    include_tags = tags if tags is not None else config.get("main", "show_problem_tags")

    save_problem(fetched_problem, keeper, rewrite, include_tags)
    if open_problem:
        keeper.open_problem(fetched_problem.title_slug)

@click.command("random")
@click.option("--difficulty", "-d", help="Problem difficulty")
@click.option("--solved", "-s", help="Include solved problems", default=False, is_flag=True)
@click.option("--rewrite", "-r", default=False, is_flag=True,
              help="Rewrite existing problem without confirmation")
@click.option('--open/--no-open', '-o/-no', default=None,
              help="Open problem in default code editor")
@click.option('--tags/--no-tags', '-t/-nt', default=None,
              help="Show problem tags (may contain solution hints)")
@pass_config
@pass_keeper
@pass_client
def random(
    client: LeetCodeClient,
    keeper: ProblemKeeper,
    config: Config,
    difficulty: str,
    solved: bool,
    rewrite: bool,
    open: Optional[bool],
    tags: Optional[bool]
):
    """Download random problem"""
    if difficulty is not None:
        if (dif := LeetCodeProblemDifficulty.from_str(difficulty)) is not None:
            difficulty = dif
        else:
            click.echo(f"Invalid difficulty: {difficulty}")
            return
    fetched_problem = None
    while fetched_problem is None:
        try:
            fetched_problem = client.get_random_problem(difficulty, solved)
        except PremiumRequired:
            sleep(1)
    open_problem = open if open is not None else config.get("main", "open_saved_problems")
    include_tags = tags if tags is not None else config.get("main", "show_problem_tags")

    save_problem(fetched_problem, keeper, rewrite, include_tags)
    if open_problem:
        keeper.open_problem(fetched_problem.title_slug)

@click.command("today")
@click.option("--rewrite", "-r", default=False, is_flag=True,
              help="Rewrite existing problem without confirmation")
@click.option('--open/--no-open', '-o/-no', default=None,
              help="Open problem in default code editor")
@click.option('--tags/--no-tags', '-t/-nt', default=None,
              help="Show problem tags (may contain solution hints)")
@pass_config
@pass_keeper
@pass_client
def today(
    client: LeetCodeClient,
    keeper: ProblemKeeper,
    config: Config,
    rewrite: bool,
    open: Optional[bool],
    tags: Optional[bool]
):
    """Download problem of today"""
    fetched_problem = client.get_problem_of_today()
    open_problem = open if open is not None else config.get("main", "open_saved_problems")
    include_tags = tags if tags is not None else config.get("main", "show_problem_tags")

    save_problem(fetched_problem, keeper, rewrite, include_tags)
    if open_problem:
        keeper.open_problem(fetched_problem.title_slug)

@click.command("plan_next")
@click.argument("PLAN")
@click.option("--rewrite", "-r", default=False, is_flag=True,
              help="Rewrite existing problem without confirmation")
@click.option('--open/--no-open', '-o/-no', default=None,
              help="Open problem in default code editor")
@click.option('--tags/--no-tags', '-t/-nt', default=None,
              help="Show problem tags (may contain solution hints)")              
@pass_config
@pass_keeper
@pass_client
def plan_next(
    client: LeetCodeClient,
    keeper: ProblemKeeper,
    config: Config,
    plan: str,
    rewrite: bool,
    open: Optional[bool],
    tags: Optional[bool]
):
    """Download next unsolved problem from LeetCode study plan\n
    PLAN: plan url or title slug"""
    plan_url_re = re.compile("leetcode\.com\/studyplan\/([\w-]+)")
    slug_re = re.compile("^[a-z0-9]+(?:-[a-z0-9]+)*$")

    if (match := plan_url_re.search(plan)) is not None:
        plan_slug = match.group(1)
    elif (match := slug_re.match(plan)) is not None:
        plan_slug = plan
    else:
        click.echo(f"Plan \"{plan}\" was not found")

    try:
        client.get_current_username()
    except AuthenticationFailed:
        raise AuthenticationFailed("Can't get current user data, next study plan problem may be incorrect, check LEETCODE_SESSION cookie.")

    fetched_problem = client.get_next_plan_problem(plan_slug)
    if fetched_problem is None:
        click.echo(f"All problems in \"{plan}\" are already solved")
        return

    open_problem = open if open is not None else config.get("main", "open_saved_problems")
    include_tags = tags if tags is not None else config.get("main", "show_problem_tags")

    save_problem(fetched_problem, keeper, rewrite, include_tags)
    if open_problem:
        keeper.open_problem(fetched_problem.title_slug)

@click.command("test")
@click.argument("PROBLEM")
@click.argument("TEST_INPUT", nargs=-1)
@click.option("--fuzzy", "-f", default=False, is_flag=True,
              help="Use fuzzy search to find the problem by name")
@pass_config
@pass_keeper
@pass_client
def test(
    client: LeetCodeClient,
    keeper: ProblemKeeper,
    config: Config,
    problem: str,
    test_input: Tuple[str],
    fuzzy: bool=False,
):
    """Test saved solution for specified problem\n
    PROBLEM: problem title or slug\n
    TEST_INPUT: testcase arguments separated by space"""
    problem_slug = slugify(problem)

    try:
        loaded_problem = LeetCodeProblem.load(problem_slug, keeper)
    except FileNotFoundError:
        loaded_problem = None
        if fuzzy and (fuz_slug := keeper.fuzzy_search_problem(problem)) is not None:
            fuz_problem = LeetCodeProblem.load(fuz_slug, keeper)
            if click.confirm(f"Are you looking for problem \"{fuz_problem.title}\" ?"):
                loaded_problem = fuz_problem

    if loaded_problem is None:
        click.echo(f"Problem \"{problem}\" was not found")
        return

    test_input = '\n'.join(test_input) if len(test_input) > 0 else None
    result = client.test_solution(loaded_problem, test_input)
    result.cut_lines(config.get("main", "max_result_line_length"))
    click.echo(result)

@click.command("submit")
@click.argument("PROBLEM")
@click.option("--fuzzy", "-f", default=False, is_flag=True,
              help="Use fuzzy search to find the problem by name")
@pass_config
@pass_keeper
@pass_client
def submit(
    client: LeetCodeClient,
    keeper: ProblemKeeper,
    config: Config,
    problem: str,
    fuzzy: bool=False
):
    """Submit saved solution for specified problem\n
    PROBLEM: problem title or slug"""
    problem_slug = slugify(problem)
    
    try:
        loaded_problem = LeetCodeProblem.load(problem_slug, keeper)
    except FileNotFoundError:
        loaded_problem = None
        if fuzzy and (fuz_slug := keeper.fuzzy_search_problem(problem)) is not None:
            fuz_problem = LeetCodeProblem.load(fuz_slug, keeper)
            if click.confirm(f"Are you looking for problem \"{fuz_problem.title}\" ?"):
                loaded_problem = fuz_problem

    if loaded_problem is None:
        click.echo(f"Problem \"{problem}\" was not found")
        return

    result = client.submit_solution(loaded_problem)
    result.cut_lines(config.get("main", "max_result_line_length"))
    click.echo(result)

@click.command("stats")
@click.argument("USERNAME", required=False)
@pass_client
def stats(client: LeetCodeClient, username: Optional[str]):
    """Get user stats\n
    USERNAME: LeetCode username, defaults to your username"""
    if username is None:
        username = client.get_current_username()
    stats = client.get_user_stats(username)
    if stats is None:
        click.echo(f"Can't get stats for user \"{username}\", try again later.")
        return
    click.echo(stats)

@click.command("clear")
@click.confirmation_option(
    "--yes", "-y",
    prompt='Are you sure you want to delete all leetcode saved problems?')
@pass_keeper
def clear(keeper: ProblemKeeper):
    """Delete all saved LeetCode problems"""
    problems_dir = keeper.problems_dir
    removed = 0 
    failed = 0
    for path in problems_dir.iterdir():
        try:
            os.remove(path)
            removed+=1
        except Exception as e:
            click.echo(f"Can't delete file at {path}: {e}")
            failed+=1
    click.echo(f"REMOVED: {removed}, FAILED: {failed}")

COMMANDS = [get, random, today, plan_next, test, submit, stats, clear]

def add_commands(group: click.Group):
    for command in COMMANDS:
        group.add_command(command)

def save_problem(
    problem: LeetCodeProblem,
    keeper: ProblemKeeper,
    rewrite: bool=False,
    include_tags: bool=True
):
    if keeper.is_problem_saved(problem.title_slug) and not rewrite:
        confirmed = click.confirm(f"Are you sure you want to rewrite problem \"{problem.title}\" ? Your solution will be lost.")
        if not confirmed:
            click.echo("Saving aborted")
            return
    saved_at = problem.save(keeper, include_tags)
    click.echo(f"Problem \"{problem.title}\" was saved at {saved_at}")