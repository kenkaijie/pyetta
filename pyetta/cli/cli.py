import pkgutil
from pathlib import Path
from types import ModuleType
from typing import Optional, Dict, Tuple

import click
from click import pass_context, Context, Parameter
from junit_xml import to_xml_report_file
from serial import Serial

from pyetta.cli.cli_helpers import cli_process_io_collector
from pyetta.cli.utils import PyettaCommand, PyettaGroup, CliState
from pyetta.loaders.interfaces import IDeviceLoader
from pyetta.loaders.pyocd import PyOCDDeviceLoader
from pyetta.parsers.interfaces import Parser

import logging
import importlib.util
import sys

from pyetta.parsers.utils import generate_exit_code

log = logging.getLogger(__name__)


def add_command_to_cli(command: PyettaCommand, command_name: Optional[str] = None) -> None:
    """Registers a command to the CLI, this is the recommended way to inject in additional commands as the mechanisms
    may change in future versions.

    :param command: The command to register
    :param command_name: Alias to call the command.
    """
    log.debug(f"Loading command '{command.name}' as '{command_name or command.name}' "
              f"from plugin '{command.plugin_name}'.")
    cli.add_command(command, command_name)


def setup_ignores(context: Context, _: Parameter, ignores: Optional[Tuple[str]] = None) -> None:
    if isinstance(context.obj, CliState):
        context.obj.plugins_filter = set(ignores)


def setup_extras(context: Context, _: Parameter, extras: Optional[Path] = None) -> None:
    if isinstance(context.obj, CliState):
        context.obj.extras = extras


def setup_logging(_: Context, __: Parameter, verbose: int):
    log_level = logging.ERROR - 10 * max(verbose, 3)
    logging.getLogger().setLevel(log_level)


def load_plugins(_: click.Group, context: Context) -> None:
    """Plugin loader for pyetta, loads all modules in scope with the pyetta_* naming format.
    Also loads the extras provided by the --extras flag.
    """
    extras = None
    plugins_filter = None
    if isinstance(context.obj, CliState):
        extras = context.obj.extras
        plugins_filter = context.obj.plugins_filter

    discovered_plugins: Dict[str, ModuleType] = {
        name: importlib.import_module(name) for _, name, _ in pkgutil.iter_modules() if name.startswith('pyetta_')
    }

    if extras is not None:
        module_name = context.obj.extras.stem
        if module_name not in plugins_filter:
            spec = importlib.util.spec_from_file_location(module_name, context.obj.extras)
            module = importlib.util.module_from_spec(spec)
            discovered_plugins[module_name] = module
            spec.loader.exec_module(module)

    for name, plugin in discovered_plugins.items():
        if name in plugins_filter:
            log.warning(f"Skipped loading plugin '{name}'.")
            continue
        logging.debug(f"Loading plugin '{name}'.")
        load_plugin = getattr(plugin, "load_plugin", None)
        if callable(load_plugin):
            try:
                load_plugin()
            except Exception as ec:
                raise ImportError(f"Error occurred while executing plugin {name}'s load_plugin function.") from ec
        else:
            raise ImportError(f"Could not call module {name}'s load_plugin function")


@click.group(chain=True, cls=PyettaGroup, pre_invoke_handler=load_plugins,
             subcommand_metavar="STAGE1 [ARGS]... [STAGE2 [ARGS]...]...")
@click.version_option()
@click.option('-v', '--verbose', help="Set verbosity",
              count=True, is_eager=True, callback=setup_logging, required=False, default=0, expose_value=False)
@click.option("-x", "--ignore-plugins", help="Name of a plugin to ignore, supports multiples.",
              required=False, type=str, callback=setup_ignores, multiple=True,
              is_eager=True, expose_value=False)
@click.option("--extras", help="Path of an extras module to load.",
              required=False, type=click.Path(exists=True, path_type=Path, dir_okay=False), callback=setup_extras,
              is_eager=True, expose_value=False)
def cli():
    """
    Python Embedded Test Toolbox and Automation

    Simple tooling to automate running tests runners on an embedded board and collecting
    output for a CI/CD server to consume.

    This command works similar to a pipeline, where we have loaders to load firmware onto a target
    and collectors to collect and parse the output to generate a test result.

    Typical flow: Loader -> Collector -> Output
    """
    pass


@cli.command("lpyocd", help="Loader for PyOCD.",
             cls=PyettaCommand, category='Loaders')
@click.option("--firmware", help="Path to the input test runner firmware.",
              type=click.Path(exists=True, path_type=Path), required=True)
@click.option("--probe", help="ID of the probe to use", required=False,
              type=str, metavar="PROBE_ID")
@click.option("--target", help="Chip target to use, must match the target connected to the host",
              required=True, type=str, metavar="TARGET_MCU")
@pass_context
def lpyocd(context: Context, firmware: Path, target: str, probe: Optional[str] = None):
    cli_state = context.find_object(CliState)
    if cli_state.loader is not None:
        raise ValueError("A device loader has already been opened. Only 1 loader at a time.")
    cli_state.loader = context.with_resource(PyOCDDeviceLoader(target=target, probe=probe))
    try:
        click.echo(f"Loading firmware {firmware} to target {target}")
        with click.progressbar(length=100, label="Flashing", show_eta=True) as progress_bar:
            def update_progress(progress: float) -> None:
                progress_pct = int(progress * 100)
                progress_bar.update(progress_pct - progress_bar.pos)

            cli_state.loader.load_firmware(firmware, update_progress=update_progress)
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
             cls=PyettaCommand, category='Collectors')
@collector_common
@pass_context
def cstdin(context: Context, parser_name: str, fail_empty: bool,
           fail_skipped: bool, junit: Optional[Path] = None):
    cli_state = context.find_object(CliState)
    loader = cli_state.loader

    try:
        click.echo(f"Execute test runner for test framework: {parser_name}")
        test_suites = cli_process_io_collector(sys.stdin, parser_name, loader=loader)
        result = Parser.generate_exit_code(test_suites, fail_empty, fail_skipped)

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
             cls=PyettaCommand, category='Collectors')
@click.option("--file", help="Path to the file with captured output.",
              type=click.Path(exists=True, path_type=Path, dir_okay=False), required=True)
@collector_common
@pass_context
def cfile(context: Context, parser_name: str, file: Path, fail_empty: bool, fail_skipped: bool,
          junit: Optional[Path] = None):
    cli_state = context.find_object(CliState)
    loader = cli_state.loader

    try:
        with open(file, "r") as fi:
            click.echo(f"Execute test runner for test framework: {parser_name}")
            test_suites = cli_process_io_collector(fi, parser_name, loader=loader)
        result = Parser.generate_exit_code(test_suites, fail_empty, fail_skipped)

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
             cls=PyettaCommand, category='Collectors')
@click.option("--baud", help="Baud rate of serial port.", default=115200,
              required=True, type=int, metavar="BAUD")
@click.option("--port", help="The serial port to use.",
              type=str, required=True, metavar="PORT")
@collector_common
@pass_context
def cserial(context: Context, parser_name: str, port: str, baud: int, fail_empty: bool,
            fail_skipped: bool, junit: Optional[Path] = None):
    cli_state = context.find_object(CliState)
    loader = cli_state.loader

    try:
        with Serial(port=port, baudrate=baud, timeout=30) as capture:
            click.echo(f"Execute test runner for test framework: {parser_name}")
            test_suites = cli_process_io_collector(capture, parser_name,
                                                   decode='ascii', loader=loader)
        result = Parser.generate_exit_code(test_suites, fail_empty, fail_skipped)

        if junit is not None:
            with open(junit, 'w') as fo:
                to_xml_report_file(fo, test_suites=test_suites, encoding='utf-8')
            click.echo(f"Results saved in file {junit}")

        click.echo(f"Execution complete, result={'PASS' if result == 0 else 'FAIL'}.")
        sys.exit(result)
    except Exception as ec:
        click.echo(f"Error executing target: {ec}")
        sys.exit(1)
