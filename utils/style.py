from enum import Enum
from typing import Dict

from click import style as click_style

from classes.exceptions import InvalidColor


class ColorType(Enum):
    TITLE = "title"
    LANGUAGE = "language"
    VALUE = "value"
    DELIMITER = "delimiter"

AVAILABLE_COLORS = {
    "black",
    "red",
    "green",
    "yellow",
    "blue",
    "magenta",
    "cyan",
    "white",
    "bright_black",
    "bright_red",
    "bright_green",
    "bright_yellow",
    "bright_blue",
    "bright_magenta",
    "bright_cyan",
    "bright_white"
}

class OutputStyler():
    colors: Dict[ColorType, str]

    def __init__(self, colors: Dict[ColorType, str]) -> None:
        for color in colors.values():
            if color not in AVAILABLE_COLORS:
                raise InvalidColor(f"Invalid color: {color}")
        self.colors = colors

    def style(self, string: str, color_type: ColorType) -> str:
        return click_style(string, fg=self.colors[color_type])
    
    def style_with_color(self, string: str, color_name: str) -> str:
        return click_style(string, fg=color_name)