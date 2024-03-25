from contextlib import suppress
from abc import ABC, abstractmethod
from typing import Dict, Any
from pathlib import Path
from json import load, loads, dump, JSONDecodeError
from dataclasses import dataclass


CONFIG_PATH: Path = Path("config.json")

class Config(ABC):

    @abstractmethod
    def get(self, *config_path: str, allow_last_none: bool=False) -> Any:
        ...
    
    @abstractmethod
    def set(self, *config_path: str, value: Any) -> None:
        ...
    
    def parse_value(self, value: str) -> Any:
        match value.lower():
            case "true":
                return True
            case "false":
                return False
            case "none" | "null":
                return None

        with suppress(JSONDecodeError, ValueError):
            return loads(value)
            return int(value)
            return float(value)
        
        return value

@dataclass()
class JsonConfig(Config):
    json_path: Path
    data: Dict[str, Any]
    
    @classmethod
    def from_path(cls: "Config", json_path: Path) -> "Config":
        with json_path.open("r", encoding="utf-8") as f:
            return cls(json_path=json_path, data=load(f))

    def get(self, *config_path: str, allow_last_none: bool=False) -> Any:
        error_str = f"Config not found: {'.'.join(config_path)}"
        current_obj = self.data
        for key in config_path:
            if current_obj is None:
                raise KeyError(error_str)
            current_obj = current_obj.get(key)
        if not allow_last_none and current_obj is None:
            raise KeyError(error_str)
        return current_obj
    
    def set(self, *config_path: str, value: Any) -> None:
        current_obj = self.data
        for key in config_path[:-1]:
            if current_obj is None:
                raise KeyError(f"Config not found: {'.'.join(config_path)}")
            current_obj = current_obj.get(key)
        current_obj[config_path[-1]] = value

        with self.json_path.open("w", encoding="utf-8") as w:
            dump(self.data, w, ensure_ascii=False, indent=2)

def get_config() -> Config:
    if not CONFIG_PATH.is_file():
        with CONFIG_PATH.open("w", encoding="utf-8") as w:
            dump(DEFAULT_CONFIG, w, ensure_ascii=False, indent=2)
    return JsonConfig.from_path(CONFIG_PATH)
    

DEFAULT_CONFIG = {
  "main": {
    "problems_dir": "problems",
    "open_saved_problems": False,
    "max_description_line_length": 88,
    "max_result_line_length": 256,
    "show_problem_tags": True,
    "colors": {
        "title": "bright_magenta",
        "language": "yellow",
        "value": "cyan",
        "delimiter": "red"
    }
  },
  "providers": {
    "leetcode": {
      "cookies_path": "leetcode_cookies.txt",
      "default_language": "Python",
      "default_shell_language": "Bash",
      "default_sql_dialect": "MySQL",
      "code_prefixes": {
        "C++": None,
        "Java": None,
        "Python": None,
        "C": None,
        "C#": None,
        "JavaScript": None,
        "TypeScript": None,
        "PHP": None,
        "Swift": None,
        "Kotlin": None,
        "Dart": None,
        "Go": None,
        "Ruby": None,
        "Scala": None,
        "Rust": None,
        "Racket": None,
        "Erlang": None,
        "Elixir": None,
        "Bash": None,
        "MySQL": None,
        "MS SQL Server": None,
        "Oracle": None,
        "PostgreSQL": None
      }
    }
  }
}