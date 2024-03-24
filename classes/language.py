from typing import List
from enum import Enum
from dataclasses import dataclass


@dataclass
class Language:
    name: str
    file_extension: str
    comment_symbol: str

    def __hash__(self) -> int:
        return hash(self.name)

class _LanguageEnum(Enum):
    
    @classmethod
    def by_name(cls, name: str) -> Language:
        for language in cls:
            if language.value.name == name:
                return language.value
        raise ValueError(f"Invalid language: {name}")

class Languages(_LanguageEnum):
    CPP = Language("C++", "cpp", "//")
    JAVA = Language("Java", "java", "//")
    PYTHON = Language("Python", "py", "#")
    C = Language("C", "c", "//")
    CSHARP = Language("C#", "cs", "//")
    JAVASCRIPT = Language("JavaScript", "js", "//")
    TYPESCRIPT = Language("TypeScript", "ts", "//")
    PHP = Language("PHP", "php", "//")
    SWIFT = Language("Swift", "swift", "//")
    KOTLIN = Language("Kotlin", "kt", "//")
    DART = Language("Dart", "dart", "//")
    GOLANG = Language("Go", "go", "//")
    RUBY = Language("Ruby", "rb", "#")
    SCALA = Language("Scala", "scala", "//")
    RUST = Language("Rust", "rs", "//")
    RACKET = Language("Racket", "rkt", ";")
    ERLANG = Language("Erlang", "erl", "%")
    ELIXIR = Language("Elixir", "exs", "#")

class ShellLanguages(_LanguageEnum):
    BASH = Language("Bash", "sh", "#")

class SQLDialects(_LanguageEnum):
    MYSQL = Language("MySQL", "sql", "--")
    MSSQL = Language("MS SQL Server", "sql", "--")
    ORACLE = Language("Oracle", "sql", "--")
    POSTGRES = Language("PostgreSQL", "sql", "--")


def any_language_by_name(name: str) -> Language:
    for lang_set in [Languages, ShellLanguages, SQLDialects]:
        try:
            return lang_set.by_name(name)
        except ValueError:
            continue
    raise ValueError(f"Invalid language: {name}")

def all_languages() -> List[Language]:
    languages = list()
    for lang_set in [Languages, ShellLanguages, SQLDialects]:
        languages.extend([lang.value for lang in lang_set])
    return languages