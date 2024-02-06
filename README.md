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
   
## Configuration
CLDojo can be configured by editing `config.json` file or using `python dojo.py config CONFIG_VAR VALUE`.

## Usage
Each command and its arguments have descriptions, use `--help` to read them.

Use `python dojo.py leetcode --help` to view leetcode-related commands.

# What's next?
Currently, only LeetCode is supported, but other platforms may be added later.
