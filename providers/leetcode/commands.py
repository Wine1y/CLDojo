import re
from time import sleep
from typing import Optional, Tuple, Set

import click
from slugify import slugify

from .client import LeetCodeClient
from .classes import LeetCodeProblemDifficulty
from providers.leetcode.classes import LeetCodeProblem
from providers.leetcode.exceptions import PremiumRequired, AuthenticationFailed
from utils.problem_keeper import ProblemKeeper
from utils.style import OutputStyler
from utils.click import pass_client, pass_keeper, pass_config, pass_default_languages, pass_styler
from utils.config import Config
from classes.language import any_language_by_name, all_languages, Language


@click.command("get")
@click.argument("PROBLEM")
@click.argument("LANGUAGE", required=False)
@click.option("--rewrite", "-r", default=False, is_flag=True,
              help="Rewrite existing problem without confirmation")
@click.option('--open/--no-open', '-o/-no', default=None,
              help="Open problem in default code editor")
@click.option('--tags/--no-tags', '-t/-nt', default=None,
              help="Show problem tags (may contain solution hints)")
@pass_default_languages(provider="leetcode")
@pass_config
@pass_keeper
@pass_client
def get(
    client: LeetCodeClient,
    keeper: ProblemKeeper,
    config: Config,
    default_languages: Set[Language],
    problem: str,
    language: Optional[str],
    rewrite: bool,
    open: Optional[bool],
    tags: Optional[bool]
):
    """Download specified problem\n
    PROBLEM: problem url or title\n
    LANGUAGE: get problem in a specified language"""
    language = [any_language_by_name(language)] if language is not None else None
    problem_url_re = re.compile("leetcode\.com\/problems\/([\w-]+)")
    if (match := problem_url_re.search(problem)) is not None:
        fetched_problem = client.get_problem(match.group(1), language or default_languages)
    else:
        fetched_problem = client.search_problem(problem, language or default_languages)

    if fetched_problem is None:
        click.echo(f"Problem \"{problem}\" was not found")
        return
    open_problem = open if open is not None else config.get("main", "open_saved_problems")
    include_tags = tags if tags is not None else config.get("main", "show_problem_tags")

    save_problem(fetched_problem, keeper, rewrite, include_tags)
    if open_problem:
        keeper.open_problem(fetched_problem.title_slug)

@click.command("random")
@click.argument("LANGUAGE", required=False)
@click.option("--difficulty", "-d", help="Problem difficulty")
@click.option("--solved", "-s", help="Include solved problems", default=False, is_flag=True)
@click.option("--rewrite", "-r", default=False, is_flag=True,
              help="Rewrite existing problem without confirmation")
@click.option('--open/--no-open', '-o/-no', default=None,
              help="Open problem in default code editor")
@click.option('--tags/--no-tags', '-t/-nt', default=None,
              help="Show problem tags (may contain solution hints)")
@pass_default_languages(provider="leetcode")
@pass_config
@pass_keeper
@pass_client
def random(
    client: LeetCodeClient,
    keeper: ProblemKeeper,
    config: Config,
    default_languages: Set[Language],
    language: Optional[str],
    difficulty: str,
    solved: bool,
    rewrite: bool,
    open: Optional[bool],
    tags: Optional[bool]
):
    """Download random problem\n
    LANGUAGE: get problem in a specified language"""
    language = [any_language_by_name(language)] if language is not None else None
    if difficulty is not None:
        if (dif := LeetCodeProblemDifficulty.from_str(difficulty)) is not None:
            difficulty = dif
        else:
            raise ValueError(f"Invalid difficulty: {difficulty}")
    fetched_problem = None
    while fetched_problem is None:
        try:
            fetched_problem = client.get_random_problem(
                language or default_languages,
                difficulty,
                solved
            )
        except PremiumRequired:
            sleep(1)
    
    open_problem = open if open is not None else config.get("main", "open_saved_problems")
    include_tags = tags if tags is not None else config.get("main", "show_problem_tags")

    save_problem(fetched_problem, keeper, rewrite, include_tags)
    if open_problem:
        keeper.open_problem(fetched_problem.title_slug)

@click.command("today")
@click.argument("LANGUAGE", required=False)
@click.option("--rewrite", "-r", default=False, is_flag=True,
              help="Rewrite existing problem without confirmation")
@click.option('--open/--no-open', '-o/-no', default=None,
              help="Open problem in default code editor")
@click.option('--tags/--no-tags', '-t/-nt', default=None,
              help="Show problem tags (may contain solution hints)")
@pass_default_languages(provider="leetcode")
@pass_config
@pass_keeper
@pass_client
def today(
    client: LeetCodeClient,
    keeper: ProblemKeeper,
    config: Config,
    default_languages: Set[Language],
    rewrite: bool,
    language: Optional[str],
    open: Optional[bool],
    tags: Optional[bool]
):
    """Download problem of today\n
    LANGUAGE: get problem in a specified language"""
    language = [any_language_by_name(language)] if language is not None else None
    fetched_problem = client.get_problem_of_today(language or default_languages)
    open_problem = open if open is not None else config.get("main", "open_saved_problems")
    include_tags = tags if tags is not None else config.get("main", "show_problem_tags")

    save_problem(fetched_problem, keeper, rewrite, include_tags)
    if open_problem:
        keeper.open_problem(fetched_problem.title_slug)

@click.command("plan_next")
@click.argument("PLAN")
@click.argument("LANGUAGE", required=False)
@click.option("--rewrite", "-r", default=False, is_flag=True,
              help="Rewrite existing problem without confirmation")
@click.option('--open/--no-open', '-o/-no', default=None,
              help="Open problem in default code editor")
@click.option('--tags/--no-tags', '-t/-nt', default=None,
              help="Show problem tags (may contain solution hints)")
@pass_default_languages(provider="leetcode")
@pass_config
@pass_keeper
@pass_client
def plan_next(
    client: LeetCodeClient,
    keeper: ProblemKeeper,
    config: Config,
    default_languages: Set[Language],
    plan: str,
    rewrite: bool,
    language: Optional[str],
    open: Optional[bool],
    tags: Optional[bool]
):
    """Download next unsolved problem from LeetCode study plan\n
    PLAN: plan url or title slug\n
    LANGUAGE: get problem in a specified language"""
    language = [any_language_by_name(language)] if language is not None else None
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

    fetched_problem = client.get_next_plan_problem(plan_slug, language or default_languages)
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
@click.argument("LANGUAGE", required=False)
@click.argument("TEST_INPUT", nargs=-1)
@click.option("--fuzzy", "-f", default=False, is_flag=True,
              help="Use fuzzy search to find the problem by name")
@pass_default_languages(provider="leetcode")
@pass_styler
@pass_config
@pass_keeper
@pass_client
def test(
    client: LeetCodeClient,
    keeper: ProblemKeeper,
    config: Config,
    styler: OutputStyler,
    default_languages: Set[Language],
    problem: str,
    language: Optional[str],
    test_input: Tuple[str],
    fuzzy: bool=False,
):
    """Test saved solution for specified problem\n
    PROBLEM: problem title or slug\n
    TEST_INPUT: testcase arguments separated by space\n
    LANGUAGE: test solution in a specified language"""
    problem_slug = slugify(problem)
    languages = [any_language_by_name(language)] if language is not None else default_languages

    for lang in languages:
        try:
            loaded_problem = LeetCodeProblem.load(problem_slug, lang, keeper)
            break
        except FileNotFoundError:
            if fuzzy and (fuz_slug := keeper.fuzzy_search_problem(problem, lang)) is not None:
                fuz_problem = LeetCodeProblem.load(fuz_slug, lang, keeper)
                if click.confirm(f"Are you looking for problem \"{fuz_problem.title}\" ({lang.name}) ?"):
                    loaded_problem = fuz_problem
                    break
    else:
        if language is not None:
            raise FileNotFoundError(f"Problem \"{problem}\" was not found in \"{language}\" directory")
        else:
            langs_str = ', '.join(lang.name for lang in default_languages)
            raise FileNotFoundError(f"Problem \"{problem}\" was not found in your default languages ({langs_str}), try providing another language")

    test_input = '\n'.join(test_input) if len(test_input) > 0 else None
    result = client.test_solution(loaded_problem, test_input)
    result.cut_lines(config.get("main", "max_result_line_length"))
    click.echo(result.styled_str(styler))

@click.command("submit")
@click.argument("PROBLEM")
@click.argument("LANGUAGE", required=False)
@click.option("--fuzzy", "-f", default=False, is_flag=True,
              help="Use fuzzy search to find the problem by name")
@pass_default_languages(provider="leetcode")
@pass_styler           
@pass_config
@pass_keeper
@pass_client
def submit(
    client: LeetCodeClient,
    keeper: ProblemKeeper,
    config: Config,
    styler: OutputStyler,
    default_languages: Set[Language],
    problem: str,
    language: Optional[str],
    fuzzy: bool=False
):
    """Submit saved solution for specified problem\n
    PROBLEM: problem title or slug\n
    LANGUAGE: submit solution in a specified language"""
    problem_slug = slugify(problem)
    languages = [any_language_by_name(language)] if language is not None else default_languages

    for lang in languages:
        try:
            loaded_problem = LeetCodeProblem.load(problem_slug, lang, keeper)
            break
        except FileNotFoundError:
            if fuzzy and (fuz_slug := keeper.fuzzy_search_problem(problem, lang)) is not None:
                fuz_problem = LeetCodeProblem.load(fuz_slug, lang, keeper)
                if click.confirm(f"Are you looking for problem \"{fuz_problem.title}\" ({lang.name}) ?"):
                    loaded_problem = fuz_problem
                    break
    else:
        if language is not None:
            raise FileNotFoundError(f"Problem \"{problem}\" was not found in \"{language}\" directory")
        else:
            langs_str = ', '.join(lang.name for lang in default_languages)
            raise FileNotFoundError(f"Problem \"{problem}\" was not found in your default languages ({langs_str}), try providing another language")

    result = client.submit_solution(loaded_problem)
    result.cut_lines(config.get("main", "max_result_line_length"))
    click.echo(result.styled_str(styler))

@click.command("stats")
@click.argument("USERNAME", required=False)
@pass_styler
@pass_client
def stats(client: LeetCodeClient, styler: OutputStyler, username: Optional[str]):
    """Get user stats\n
    USERNAME: LeetCode username, defaults to your username"""
    if username is None:
        username = client.get_current_username()
    stats = client.get_user_stats(username)
    if stats is None:
        click.echo(f"Can't get stats for user \"{username}\", try again later.")
        return
    click.echo(stats.styled_str(styler))

@click.command("clear")
@click.option("--yes", "-y",is_flag=True, help="Skip the confirmation prompt")
@click.argument("LANGUAGE", required=False)
@pass_styler
@pass_keeper
def clear(keeper: ProblemKeeper, styler: OutputStyler, yes: bool, language: Optional[str]=None):
    """Delete all saved LeetCode problems\n
    LANGUAGE: Delete problems in specified language"""
    language = any_language_by_name(language) if language is not None else None
    if not yes:
        if language is None:
            click.confirm("Are you sure you want to delete all leetcode problems ?", abort=True)
        else:
            click.confirm(f"Are you sure you want to delete all leetcode problems in {language.name} ?", abort=True)

    if language is not None:
        removed, failed = keeper.delete_problems(language)
    else:
        removed = failed = 0
        for language in all_languages():
            lang_removed, lang_failed = keeper.delete_problems(language)
            removed+=lang_removed
            failed+=lang_failed
    removed = styler.style_with_color(removed, 'bright_green')
    failed = styler.style_with_color(failed, 'bright_red')
    
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
    if keeper.is_problem_saved(problem.title_slug, problem.language) and not rewrite:
        confirmed = click.confirm(f"Are you sure you want to rewrite problem \"{problem.title}\" ? Your solution will be lost.")
        if not confirmed:
            click.echo("Saving aborted")
            return
    saved_at = problem.save(keeper, include_tags)
    click.echo(f"Problem \"{problem.title}\" was saved at {saved_at}")