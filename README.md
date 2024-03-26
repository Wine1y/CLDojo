# What?
**CLDojo** is a command line tool which allows you to solve LeetCode questions without leaving your favorite IDE.

# Why?
It's not so nice to use LeetCode web editor when you're addicted to IDE features like autocomplete, macros, error checking, is it ?
Now you can download any problem you need with one command, solve it in your editor and then test or submit your solution with another command.

So, wrapping up:
1. It's more convenient to use your editor of choice
2. It's faster to use CLI to test/submit solutions than the web GUI
3. Web editor doesn't support your favorite neon theme (the most important)
# How?
## Installation
1. Install requirements with `pip install -r requirements.txt`
2. Use dojo.py to access required CLI commands

## Usage
Each command and its arguments have descriptions, use `--help` to read them.

Use `python dojo.py leetcode --help` to view leetcode-related commands.

## Configuration
CLDojo can be configured by editing `config.json` file or using `python dojo.py config CONFIG_VAR VALUE`.

Configuration can be reset by deleting `config.json` file.

|                 **Config**                | **Value Type** |                                                **Description**                                                |
|:-----------------------------------------:|:--------------:|:-------------------------------------------------------------------------------------------------------------:|
|                problems_dir               |     _path_     |                                 Path where downloaded problems will be stored                                 |
|            open_saved_problems            |     _bool_     |                         If set to 'true', problems will open in default editor on save                        |
|           max_result_line_length          |      _int_     |       Maximum result line length, extra characters will be trimmed (can be used to trim long test cases)      |
|        max_description_line_length        |      _int_     | Maximum description line length, extra characters will be wrapped. If set to 0, description lines won't wrap. |
|             show_problem_tags             |     _bool_     |           If set to 'false', saved problems won't include tags. Tags may contain hints for solution.          |
|                   colors                  |      _obj_     |                         Colors for various output elements. Only ASCII colors allowed.                        |
|      providers.leetcode.cookies_path      |     _path_     |                         Path to leetcode cookies file in netscape cookies file format                         |
|    providers.leetcode.default_languages   |    _string_    |                        Default language to use when downloading or submitting problems                        |
| providers.leetcode.default_shell_language |    _string_    |                   Default language to use when downloading or submitting **shell** problems                   |
|   providers.leetcode.default_sql_dialect  |    _string_    |                  Default language to use when downloading or submitting **database** problems                 |
|      providers.leetcode.code_prefixes     |      _obj_     |       Code prefixes for supported languages. For example `from typing import *` can be used for Python.       |

## Commands
Arguments in **bold** font are required.

|     **Command**    |             **Arguments**             |                     **Description**                     |
|:------------------:|:-------------------------------------:|:-------------------------------------------------------:|
|    leetcode get    |        **PROBLEM**, _LANGUAGE_        |           Download specified LeetCode problem           |
|   leetcode random  |               _LANGUAGE_              |             Download random LeetCode problem            |
|   leetcode today   |               _LANGUAGE_              |            Download LeetCode problem of today           |
| leetcode plan_next |          **PLAN**, _LANGUAGE_         | Download next unsolved problem from LeetCode study plan |
|    leetcode test   | **PROBLEM**, _LANGUAGE_, _TEST_INPUT_ |    Test saved solution for specified LeetCode problem   |
|   leetcode submit  |        **PROBLEM**, _LANGUAGE_        |   Submit saved solution for specified LeetCode problem  |
|   leetcode stats   |               _USERNAME_              |                 Get LeetCode user stats                 |
|   leetcode clear   |               _LANGUAGE_              |             Delete saved LeetCode problems.             |

# What's next?
Currently, only LeetCode is supported, but other platforms may be added later.
