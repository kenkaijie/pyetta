import logging

from pyetta.cli.cli import cli

logging.basicConfig(level=logging.ERROR)


def main():
    cli(auto_envvar_prefix="PYETTA")


# no need to check if name is main, as our file name is explicit.
main()
