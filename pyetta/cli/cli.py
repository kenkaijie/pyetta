import importlib.util
import logging
from pathlib import Path
from types import ModuleType
from typing import Optional, Tuple, Callable, Dict, List, Union

import click
from click import pass_context, Context, Parameter

from pyetta.cli.utils import PyettaCommand, PyettaCLIRoot, CliState, ExecutionPipeline, \
    ExecutionCallable

from importlib_metadata import entry_points, EntryPoint

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
                 extras: Optional[Tuple[Path]] = None) -> None:
    context.ensure_object(CliState)
    context.obj.extras = set(extras)


def setup_logging(_: Context, __: Parameter, verbose: int):
    log_level = logging.ERROR - (10 * min(verbose, 3))
    logging.getLogger().setLevel(log_level)


def load_plugins(_: click.Group, context: Context) -> None:
    """Plugin loader for pyetta, loads all modules in scope with the pyetta_*
    naming format. Also loads the extras provided by the --extras flag.
    """
    context.ensure_object(CliState)

    plugin_entry_points: Dict[str, Union[Callable[[], None], ModuleType]] = dict()

    for entry_point in entry_points(group="pyetta.plugins"):  # type: EntryPoint
        if entry_point.name in plugin_entry_points:
            log.warning(f"pyetta found 2 modules with the same name! {entry_point.name}. We are "
                        f"only loading the first one.")
        else:
            plugin = entry_point.load()
            plugin_entry_points[entry_point.name] = plugin

    for extra in context.obj.extras:
        module_name = extra.stem
        if module_name in plugin_entry_points:
            log.warning(f"pyetta found 2 modules with the same name! {module_name}. We are only "
                        f"loading the first one.")
        else:
            spec = importlib.util.spec_from_file_location(module_name, extra)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            plugin_entry_points[module_name] = module

    for name, loaded in plugin_entry_points.items():
        if name in context.obj.plugins_filter:
            log.warning(f"Skipped loading plugin '{name}'.")
            continue
        log.debug(f"Loading plugin '{name}'.")
        try:
            loaded = getattr(loaded, "load_plugin")
            loaded()
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
              required=False, multiple=True,
              type=click.Path(exists=True, path_type=Path, dir_okay=False),
              callback=setup_extras,
              is_eager=True, expose_value=False)
def cli() -> None:
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
            chunk = plan.collector.read_chunk()

            if chunk is not None and len(chunk) > 0:
                click.echo(chunk)
                plan.parser.feed_data(chunk)
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

        # our logic just takes the highest exit code it can
        exit_code = max(reporter_exit_code, exit_code)

    context.exit(exit_code)
