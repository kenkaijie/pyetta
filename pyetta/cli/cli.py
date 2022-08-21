import contextlib
import importlib.util
import io
import logging
import sys
from pathlib import Path
from typing import Optional, Tuple, Callable, Dict, List, ContextManager, cast

import click
from click import pass_context, Context, Parameter
from serial import Serial

from pyetta.cli.utils import PyettaCommand, PyettaCLIRoot, CliState, \
    ExecutionPipeline, \
    execution_config, ExecutionCallable
from pyetta.loaders import PyOCDDeviceLoader
from pyetta.parsers import UnityParser
from pyetta.reporters import JUnitXmlReporter

if sys.version_info < (3, 10):
    from importlib_metadata import entry_points, EntryPoint
else:
    from importlib.metadata import entry_points, EntryPoint

log = logging.getLogger("pyetta.cli")


def add_command_to_cli(command: PyettaCommand,
                       command_name: Optional[str] = None) -> None:
    """Registers a command to the CLI, this is the recommended way to inject
    in additional commands as the mechanisms may change in future versions.

    :param command: The command to register
    :param command_name: Alias to call the command.
    """
    log.debug(
        f"Loading '{command.name}' as '{command_name or command.name}' "
        f"from plugin '{command.plugin_name}'.")
    cli.add_command(command, command_name)


def setup_ignores(context: Context, _: Parameter,
                  ignores: Optional[Tuple[str]] = None) -> None:
    context.ensure_object(CliState)
    context.obj.plugins_filter = set(ignores)


def setup_extras(context: Context, _: Parameter,
                 extras: Optional[Path] = None) -> None:
    context.ensure_object(CliState)
    context.obj.extras = extras


def setup_logging(_: Context, __: Parameter, verbose: int):
    log_level = logging.ERROR - (10 * min(verbose, 3))
    logging.getLogger().setLevel(log_level)


def load_plugins(_: click.Group, context: Context) -> None:
    """Plugin loader for pyetta, loads all modules in scope with the pyetta_*
    naming format. Also loads the extras provided by the --extras flag.
    """
    context.ensure_object(CliState)

    plugin_entry_points: Dict[str, Callable[[], None]] = dict()

    for entry_point in entry_points(group="pyetta.plugin",
                                    name="load_plugin"):  # type: EntryPoint
        load_plugin = entry_point.load()
        plugin_entry_points[entry_point.module] = load_plugin

    if context.obj.extras is not None:
        module_name = context.obj.extras.stem
        spec = importlib.util.spec_from_file_location(module_name,
                                                      context.obj.extras)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        plugin_entry_points[module_name] = getattr(module, "load_plugin",
                                                   lambda: None)

    for name, load_function in plugin_entry_points.items():
        if name in context.obj.plugins_filter:
            log.warning(f"Skipped loading plugin '{name}'.")
            continue
        log.debug(f"Loading plugin '{name}'.")
        try:
            load_function()
        except Exception as ec:
            raise ImportError(
                f"Error occurred while executing plugin {name}'s load_plugin "
                "entry point. If you cannot uninstall the plugin, use the -x "
                "flag to ignore loading of the offending plugin.") from ec


@click.group(chain=True, cls=PyettaCLIRoot, plugin_handler=load_plugins,
             subcommand_metavar="STAGE1 [ARGS]... [STAGE2 [ARGS]...]...")
@click.version_option(message="%(version)s")
@click.option('-v', 'verbose',
              help="Sets verbosity. Can be repeated up to 3 times.",
              count=True, callback=setup_logging, required=False, default=0,
              is_eager=True, expose_value=False)
@click.option("--exclude-plugins",
              help="Plugin to exclude from loading, supports multiples.",
              required=False, type=str, callback=setup_ignores, multiple=True,
              is_eager=True, expose_value=False, metavar="MODULE_NAME")
@click.option("--extras", help="Path of an extras module to load.",
              required=False,
              type=click.Path(exists=True, path_type=Path, dir_okay=False),
              callback=setup_extras,
              is_eager=True, expose_value=False)
def cli():
    """Python Embedded Test Toolbox and Automation

    Simple tooling to automate running tests runners on an embedded board and
    collecting output for a CI/CD server to consume.

    This command works similar to a pipeline, where we have loaders to load
    firmware onto a target and collectors to collect and parse the output to
    generate a test result.

    An execution plan requires a Loader, a Collector, a Parser, and [1-N]
    Reporters.
    """


@cli.result_callback()
@pass_context
def cli_execute_plan(context: Context,
                     setup_functions: List[ExecutionCallable]) -> None:
    log.debug("Entering execution phase.")
    plan = ExecutionPipeline()

    for setup_function in setup_functions:
        setup_function(context, plan)

    if not plan.is_valid():
        raise ValueError("Execution plan missing 1 or more required stages.")

    log.debug("Loaded all execution objects.")

    try:
        click.echo(f"Loading with loader {plan.loader}.")
        with click.progressbar(length=100, label="Flashing",
                               show_eta=True) as progress_bar:
            def update_progress(progress: float) -> None:
                progress_pct = int(progress * 100)
                progress_bar.update(progress_pct - progress_bar.pos)

            plan.loader.load_to_device(progress=update_progress)
    except Exception as ec:
        log.debug("Error loading firmware to target.", exc_info=ec)
        raise click.ClickException(str(ec)) from ec

    try:
        click.echo("Executing test runner.")

        plan.loader.start_program()

        done = False
        while not done:
            line_bytes = plan.collector.readline()

            if line_bytes is not None and len(line_bytes) > 0:
                click.echo(line_bytes)
                plan.parser.feed_data(line_bytes)
            else:
                plan.parser.stop()

            done = plan.parser.done

    except Exception as ec:
        log.debug("Error collecting data from target.", exc_info=ec)
        raise click.ClickException(str(ec)) from ec

    # pass test suites to reports

    exit_code = 0
    for reporter in plan.reporters:
        reporter_exit_code = reporter.generate_report(plan.parser.test_suites)
        exit_code = max(reporter_exit_code, exit_code)

    context.exit(exit_code)


@cli.command("lpyocd", help="Loader for PyOCD.",
             cls=PyettaCommand, category='Loaders')
@click.option("--firmware", help="Path to the input test runner firmware.",
              type=click.Path(exists=True, path_type=Path), required=True)
@click.option("--probe", help="ID of the probe to use", required=False,
              type=str, metavar="PROBE_ID")
@click.option("--target",
              help="Chip target, must match the target connected to the host",
              required=True, type=str, metavar="TARGET_MCU")
def lpyocd(firmware: Path, target: str,
           probe: Optional[str] = None) -> ExecutionCallable:
    """Loader that uses pyocd to service the flashing of firmware to the board.
    Note for this loader to work, pyocd must be loaded with the correct boards
    and debuggers.
    """

    @execution_config
    def configure_pipeline(context: Context,
                           pipeline: ExecutionPipeline) -> None:
        loader = PyOCDDeviceLoader(target=target, probe=probe,
                                   firmware_path=firmware)
        pipeline.loader = loader
        context.with_resource(loader)

    return configure_pipeline


@cli.command("cstdin", help="Collector for standard input.",
             cls=PyettaCommand, category='Collectors')
def cstdin() -> ExecutionCallable:
    """Collector to extract information from standard in. Used if piping the
    data from the device via a shell pipe.
    """

    @execution_config
    def configure_pipeline(context: Context,
                           pipeline: ExecutionPipeline) -> None:
        @contextlib.contextmanager
        def stdin_dummy_context():
            pipeline.collector = sys.stdin
            yield

        context.with_resource(stdin_dummy_context())

    return configure_pipeline


@cli.command("cfile", help="Collector for file output.",
             cls=PyettaCommand, category='Collectors')
@click.option("--file", help="Path to the file with captured output.",
              type=click.Path(exists=True, path_type=Path, dir_okay=False),
              required=True)
@click.option("-e", "--encoding", help="file encoding to open the file with.",
              default='utf-8')
def cfile(file: Path, encoding: str = 'utf-8') -> ExecutionCallable:
    @execution_config
    def configure_pipeline(context: Context,
                           pipeline: ExecutionPipeline) -> None:
        file_obj = io.open(file=file, mode="r", encoding=encoding)
        pipeline.collector = file_obj
        context.with_resource(file_obj)

    return configure_pipeline


@cli.command("cserial", help="Collector for serial based test output.",
             cls=PyettaCommand, category='Collectors')
@click.option("--baud", help="Baud rate of serial port.", default=115200,
              required=True, type=int, metavar="BAUD")
@click.option("--port", help="The serial port to use.",
              type=str, required=True, metavar="PORT")
def cserial(port: str, baud: int) -> ExecutionCallable:
    @execution_config
    def configure_pipeline(context: Context,
                           pipeline: ExecutionPipeline) -> None:
        serial = cast(Serial(port=port, baudrate=baud, timeout=5),
                      ContextManager[Serial])
        pipeline.collector = serial
        context.with_resource(serial)

    return configure_pipeline


@cli.command("punity", help="Parser for the Unity unit test framework.",
             cls=PyettaCommand, category="Parsers")
@click.option("--name", help="optional name of this test suite",
              type=str, metavar="TEST_SUITE_NAME")
def punity(name: Optional[str] = None) -> ExecutionCallable:
    @execution_config
    def configure_pipeline(context: Context,
                           pipeline: ExecutionPipeline) -> None:
        parser = UnityParser(name)
        pipeline.parser = parser
        context.with_resource(parser)

    return configure_pipeline


@cli.command("ojunitxml", help="JUnit XML output reporter.",
             cls=PyettaCommand, category="Outputters")
@click.option("--file", "file_path", help="Output file path.", required=True,
              type=click.Path(path_type=Path))
@click.option("--fail-on-skipped", "fail_skipped",
              help="Returns a failure exit code if any tests are skipped.",
              is_flag=True, default=True, type=bool)
@click.option("--fail-on-empty", "fail_empty",
              help="Returns a failure exit code if no tests were detected.",
              is_flag=True, default=True, type=bool)
def ojunitxml(file_path: Path, fail_skipped: bool = True,
              fail_empty: bool = True) -> \
        ExecutionCallable:
    @execution_config
    def configure_pipeline(context: Context,
                           pipeline: ExecutionPipeline) -> None:
        reporter = JUnitXmlReporter(file_path=file_path,
                                    fail_on_skipped=fail_skipped,
                                    fail_on_empty=fail_empty)
        pipeline.reporters.append(reporter)
        context.with_resource(reporter)

    return configure_pipeline
