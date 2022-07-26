#!/usr/bin/env python
# TODO:
#       - Revise the CLI, refactor loaders and captures as well to a similar style as parsers
#       - Implement publishing
#       - Separate CLI commands from the entry script (do it via a cli folder instead)
#       - Automate releases to github and publishing to pypi?

import logging

from pyetta.cli.cli import cli

logging.basicConfig(level=logging.ERROR)


def main():
    cli(auto_envvar_prefix="PYETTA")


if __name__ == '__main__':
    main()
