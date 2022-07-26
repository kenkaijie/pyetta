import sys
from pathlib import Path
from typing import Optional

import click
from click import pass_context, Context
from junit_xml import to_xml_report_file
from serial import Serial

from pyetta.cli.cli_helpers import cli_process_io_collector
from pyetta.cli.utils import CategorisedCommand, root_context, CategorisedHelp, ExecutionResources
from pyetta.loaders.interfaces import IDeviceLoader
from pyetta.loaders.pyocd import PyOCDDeviceLoader

import logging

from pyetta.parsers.utils import result_from_test_suites

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

    Typical flow: Loader -> Collector -> Output
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


def collector_common(func):
    @click.option("--parser", "parser_name", metavar="NAME",
                  help="Name of test framework. See parsers command for available parsers.",
                  required=True, multiple=False, type=str)
    @click.option("--junit", help="Output a Junit XML file.", default=None,
                  type=click.Path(file_okay=True, dir_okay=False, writable=True, path_type=Path))
    @click.option("--fail-empty/--no-fail-empty", is_flag=True, default=True,
                  help="Causes the test execution to return failure if it ran no tests.")
    @click.option("--fail-skipped/--no-fail-skipped", is_flag=True, default=False,
                  help="Causes the test execution to return failure if it has to skip tests.")
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
    return wrapper


@cli.command("cstdin", help="Collector for standard input.",
             cls=CategorisedCommand, category='Collectors')
@collector_common
@pass_context
def cstdin(context: Context, parser_name: str, fail_empty: bool,
           fail_skipped: bool, junit: Optional[Path] = None):
    root = root_context(context)
    loader: Optional[IDeviceLoader] = root.obj.loader

    try:
        click.echo(f"Execute test runner for test framework: {parser_name}")
        test_suites = cli_process_io_collector(sys.stdin, parser_name, loader=loader)
        result = result_from_test_suites(test_suites, fail_empty, fail_skipped)

        if junit is not None:
            with open(junit, 'w') as fo:
                to_xml_report_file(fo, test_suites=test_suites, encoding='utf-8')
            click.echo(f"Results saved in file {junit}")

        click.echo(f"Execution complete, result={'PASS' if result == 0 else 'FAIL'}.")
        sys.exit(result)
    except Exception as ec:
        click.echo(f"Error executing target: {ec}")
        sys.exit(1)


@cli.command("cfile", help="Collector for file output.",
             cls=CategorisedCommand, category='Collectors')
@click.option("--file", help="Path to the file with captured output.",
              type=click.Path(exists=True, path_type=Path, dir_okay=False), required=True)
@collector_common
@pass_context
def cfile(context: Context, parser_name: str, file: Path, fail_empty: bool,
          fail_skipped: bool, junit: Optional[Path] = None):
    root = root_context(context)
    loader: Optional[IDeviceLoader] = root.obj.loader

    try:
        with open(file, "r") as fi:
            click.echo(f"Execute test runner for test framework: {parser_name}")
            test_suites = cli_process_io_collector(fi, parser_name, loader=loader)
        result = result_from_test_suites(test_suites, fail_empty, fail_skipped)

        if junit is not None:
            with open(junit, 'w') as fo:
                to_xml_report_file(fo, test_suites=test_suites, encoding='utf-8')
            click.echo(f"Results saved in file {junit}")

        click.echo(f"Execution complete, result={'PASS' if result == 0 else 'FAIL'}.")
        sys.exit(result)
    except Exception as ec:
        click.echo(f"Error executing target: {ec}")
        sys.exit(1)


@cli.command("cserial", help="Collector for serial based test output.",
             cls=CategorisedCommand, category='Collectors')
@click.option("--baud", help="Baud rate of serial port.", default=115200,
              required=True, type=int, metavar="BAUD")
@click.option("--port", help="The serial port to use.",
              type=str, required=True, metavar="PORT")
@collector_common
@pass_context
def cserial(context: Context, parser_name: str, port: str, baud: int, fail_empty: bool,
            fail_skipped: bool, junit: Optional[Path] = None):
    root = root_context(context)
    loader: Optional[IDeviceLoader] = root.obj.loader

    try:
        with Serial(port=port, baudrate=baud, timeout=30) as capture:
            click.echo(f"Execute test runner for test framework: {parser_name}")
            test_suites = cli_process_io_collector(capture, parser_name,
                                                   decode='ascii', loader=loader)
        result = result_from_test_suites(test_suites, fail_empty, fail_skipped)

        if junit is not None:
            with open(junit, 'w') as fo:
                to_xml_report_file(fo, test_suites=test_suites, encoding='utf-8')
            click.echo(f"Results saved in file {junit}")

        click.echo(f"Execution complete, result={'PASS' if result == 0 else 'FAIL'}.")
        sys.exit(result)
    except Exception as ec:
        click.echo(f"Error executing target: {ec}")
        sys.exit(1)
