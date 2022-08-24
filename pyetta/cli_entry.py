#!/usr/bin/env python
import logging

from pyetta.cli.cli import cli

logging.basicConfig(level=logging.ERROR)


def main():
    cli(auto_envvar_prefix="PYETTA")


if __name__ == '__main__':
    main()
