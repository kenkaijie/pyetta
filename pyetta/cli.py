#!/usr/bin/env python

from typing import Optional

# TODO:
#       - Revise the CLI, refactor loaders and captures as well to a similar style as parsers
#       - Implement publishing
#       - Separate CLI commands from the entry script (do it via a cli folder instead)
#       - Implement some unit testing
#       - Automate releases to github and publishing to pypi?

import click
import sys

from prettytable import PrettyTable, prettytable
from serial import Serial

from pyetta.loaders.pyocd_loader import PyOCDLoader
from pyetta.parsers.parser_factory import ParserFactory

import logging

logging.basicConfig(level=logging.ERROR)
log = logging.getLogger(__name__)


def setup_standard_table_config(table: PrettyTable):
    table.align = 'l'
    table.header = True
    table.border = True
    table.hrules = prettytable.HEADER
    table.vrules = prettytable.NONE


@click.group()
@click.version_option()
def cli():
    """
    Python Embedded Test Toolbox and Automation

    Simple tooling to automate running tests runners on an embedded board and collecting
    output for a CI/CD server to consume.
    """
    pass


@cli.command("probes", help="Lists all the probes connected to the host.")
def probes():
    PyOCDLoader.list_targets()


@cli.command("parsers", help="Lists details about a specific parser or all parsers.")
@click.option("--csv", help="Print in a CSV format.", is_flag=True, default=False)
@click.argument("name", required=False, metavar="NAME", type=str)
def parsers(csv: bool, name: Optional[str] = None):

    table = prettytable.PrettyTable(["Parser Name", "Description"])
    setup_standard_table_config(table)

    if name is None:
        for parser_name, parser in ParserFactory.supported_parsers():
            table.add_row([parser_name, parser.__doc__])
    else:
        table.add_row([name, ParserFactory.get_parser_type_by_name(name).__doc__])

    click.echo(table.get_csv_string() if csv else table)


@cli.command("serial", help="Runs the python test runner with a serial monitor to capture output.")
@click.option("--firmware", help="Path to the input test runner firmware.",
              type=click.Path(exists=True, path_type=str), required=True)
@click.option("--parser", "parser_creation_string", metavar="CREATION_STRING",
              help="Parser construction string, a comma separated key value pair. See parsers "
                   "command for usage.",
              required=True, multiple=False, type=str)
@click.option("--probe", help="ID of the probe to use", required=False,
              type=str, metavar="PROBE_ID")
@click.option("--baud", help="Baud rate of monitor comms",
              required=True, type=int, metavar="BAUD")
@click.option("--target", help="Chip target to use, must match the target connected to the host",
              required=True, type=str, metavar="TARGET_MCU")
@click.option("--port", help="The serial port to use.",
              type=str, required=True, metavar="PORT")
def serial(firmware: str, parser_creation_string: str, port: str, baud: int,
           target: str, probe: Optional[str] = None):

    loader = PyOCDLoader(target=target, probe=probe)

    try:
        click.echo(f"Loading firmware {firmware} to target {target}")
        with click.progressbar(length=100, label="Flashing", show_eta=True) as progress_bar:
            def update_progress(progress: float) -> None:
                progress_pct = int(progress * 100)
                progress_bar.update(progress_pct - progress_bar.pos)
            loader.load_program(firmware, progress=update_progress)
    except Exception as ec:
        log.exception(ec, exc_info=ec)
        click.echo(f"Error loading firmware to target: {repr(ec)}")
        sys.exit(1)
    else:
        click.echo("Loading completed.")

    result = None

    try:
        parser = ParserFactory.create_by_creation_string(parser_creation_string)
        click.echo(f"Execute test runner for test framework: {parser.name}")

        with Serial(port=port, baudrate=baud, timeout=30) as capture:
            loader.start_program()

            while result is None:
                read_bytes = capture.readline()

                if read_bytes is not None and len(read_bytes) > 0:
                    ascii_string = read_bytes.decode('ascii').strip('\r\n')
                    click.echo(ascii_string)
                    result = parser.scan_line(ascii_string)
                else:
                    result = parser.done()
            if result is None:
                result = 2

    except Exception as ec:
        click.echo(f"Error executing target: {ec}")
        sys.exit(1)
    else:
        click.echo(f"Execution complete, result={'PASS' if result == 0 else 'FAIL'}.")

    sys.exit(result)


def main():
    cli(auto_envvar_prefix="PYETTA")


if __name__ == '__main__':
    main()
