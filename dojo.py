from pathlib import Path
from typing import Optional

import click

from providers.leetcode.commands import add_commands as add_leetcode_commands
from providers.leetcode.client import LeetCodeClient
from utils.click import pass_config
from utils.problem_keeper import ProblemKeeper
from utils.problem_formatter import ProblemFormatter
from utils.config import Config, get_config
from utils.style import OutputStyler, ColorType, AVAILABLE_COLORS


@click.group()
@click.pass_context
def dojo(ctx):
    ctx.ensure_object(dict)
    ctx.obj['config'] = get_config()

@dojo.command("config")
@click.argument("CONFIG_PATH")
@click.argument("SET_VALUE", required=False)
@pass_config
def config(config: Config, config_path: str, set_value: Optional[str]):
    """Get or set any config value\n
    CONFIG_PATH: path to config entry, dot-separated\n
    SET_VALUE: value to set"""
    path_list = config_path.split(".")
    try:
        if set_value is None:
            click.echo(config.get(*path_list))
        else:
            config.set(*path_list, value=config.parse_value(set_value))
    except KeyError:
        click.echo(f"Config not found: {config_path}")
        return

@dojo.group()
@pass_config
@click.pass_context
def leetcode(ctx, config: Config):
    """Use LeetCode API to get problems and test/submit their solutions"""
    ctx.ensure_object(dict)
    
    formatter = ProblemFormatter(
        max_description_line_length=config.get("main", "max_description_line_length"),
        code_prefixes=config.get("providers", "leetcode", "code_prefixes")
    )
    styler = OutputStyler({
        ColorType.TITLE: config.get("main", "colors", "title"),
        ColorType.LANGUAGE: config.get("main", "colors", "language"),
        ColorType.VALUE: config.get("main", "colors", "value"),
        ColorType.DELIMITER: config.get("main", "colors", "delimiter")
    })
    client = LeetCodeClient(
        cookies_file_path=Path(config.get("providers", "leetcode", "cookies_path"))
    )
    keeper = ProblemKeeper(
        provider="leetcode",
        formatter=formatter,
        problems_path=Path(config.get("main", "problems_dir", allow_last_none=True)),
        
    )

    ctx.obj['styler'] = styler
    ctx.obj['client'] = client
    ctx.obj['keeper'] = keeper


if __name__ == "__main__":
    add_leetcode_commands(leetcode)
    dojo()