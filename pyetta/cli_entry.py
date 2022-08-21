#!/usr/bin/env python
import logging

from pyetta.cli.cli import cli
from pyetta.cli.utils import CliState

logging.basicConfig(level=logging.ERROR)


def main():
    cli(auto_envvar_prefix="PYETTA", obj=CliState())


if __name__ == '__main__':
    main()
