import sys
from pathlib import Path
from typing import Optional

import click
from click import pass_context, Context
from junit_xml import to_xml_report_file
from serial import Serial

from pyetta.cli.utils import CategorisedHelp, CategorisedCommand, ExecutionResources, root_context
from pyetta.loaders.interfaces import IDeviceLoader
from pyetta.loaders.pyocd import PyOCDDeviceLoader
from pyetta.parsers.builder import ParserBuilder
from pyetta.parsers.utils import result_from_test_suites


import logging

log = logging.getLogger(__name__)


@click.group(chain=True, cls=CategorisedHelp)
@click.version_option()
@pass_context
def cli(context: Context):
    """
    Python Embedded Test Toolbox and Automation

    Simple tooling to automate running tests runners on an embedded board and collecting
    output for a CI/CD server to consume.

    This command works similar to a pipeline, where we have loaders to load firmware onto a target
    and collectors to collect and parse the output to generate a test result.

    Typical flow: Loader -> Collector
    """
    context.obj = ExecutionResources()


@cli.command("lpyocd", help="Loader for PyOCD.",
             cls=CategorisedCommand, category='Loaders')
@click.option("--firmware", help="Path to the input test runner firmware.",
              type=click.Path(exists=True, path_type=Path), required=True)
@click.option("--probe", help="ID of the probe to use", required=False,
              type=str, metavar="PROBE_ID")
@click.option("--target", help="Chip target to use, must match the target connected to the host",
              required=True, type=str, metavar="TARGET_MCU")
@pass_context
def lpyocd(context: Context, firmware: Path, target: str, probe: Optional[str] = None):
    root = root_context(context)
    if root.obj.loader is not None:
        raise ValueError("A device loader has already been opened. Only 1 loader at a time.")
    root.obj.loader = root.with_resource(PyOCDDeviceLoader(target=target, probe=probe))
    try:
        click.echo(f"Loading firmware {firmware} to target {target}")
        with click.progressbar(length=100, label="Flashing", show_eta=True) as progress_bar:
            def update_progress(progress: float) -> None:
                progress_pct = int(progress * 100)
                progress_bar.update(progress_pct - progress_bar.pos)
            root.obj.loader.load_firmware(firmware, progress=update_progress)
    except Exception as ec:
        log.exception(ec, exc_info=ec)
        click.echo(f"Error loading firmware to target: {repr(ec)}")
        sys.exit(1)
    else:
        click.echo("Loading completed.")


@cli.command("cserial", help="Collector for serial based test output.",
             cls=CategorisedCommand, category='Collectors')
@click.option("--parser", metavar="NAME",
              help="Name of test framework. See parsers command for available parsers.",
              required=True, multiple=False, type=str)
@click.option("--baud", help="Baud rate of serial port.", default=115200,
              required=True, type=int, metavar="BAUD")
@click.option("--port", help="The serial port to use.",
              type=str, required=True, metavar="PORT")
@click.option("--junit", help="Output a Junit XML file.", default=None,
              type=click.Path(file_okay=True, dir_okay=False, writable=True, path_type=Path))
@pass_context
def cserial(context: Context, parser: str, port: str, baud: int, junit: Optional[Path] = None):
    root = root_context(context)
    loader: Optional[IDeviceLoader] = root.obj.loader

    try:
        parser = ParserBuilder.from_name(parser)
        click.echo(f"Execute test runner for test framework: {parser}")

        with Serial(port=port, baudrate=baud, timeout=30) as capture:
            if loader is not None:
                loader.start_program()

            while not parser.done:
                read_bytes = capture.readline()

                if read_bytes is not None and len(read_bytes) > 0:
                    ascii_string = read_bytes.decode('ascii').strip('\r\n')
                    click.echo(ascii_string)
                    parser.scan_line(ascii_string)
                else:
                    parser.abort()

            test_suites = parser.test_suites
            result = result_from_test_suites(test_suites)

            if result == 0 and junit is not None:
                with open(junit, 'w') as fo:
                    to_xml_report_file(fo, test_suites=test_suites, encoding='utf-8')
                click.echo(f"Results saved in file {junit}")

            click.echo(f"Execution complete, result={'PASS' if result == 0 else 'FAIL'}.")
            sys.exit(result)
    except Exception as ec:
        click.echo(f"Error executing target: {ec}")
        sys.exit(1)
