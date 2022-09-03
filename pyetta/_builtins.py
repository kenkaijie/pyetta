"""Provides the base built-in stages for use.

This file creates null version of all systems. This module is loaded via the plugin mechanism.
"""
import io
from pathlib import Path
from typing import Callable, Optional

import click
from click import Context
from serial import Serial

from pyetta.cli.cli import add_command_to_cli
from pyetta.cli.utils import PyettaCommand, ExecutionCallable, execution_config, ExecutionPipeline
from pyetta.collectors import IOBaseCollector
from pyetta.loaders import Loader, PyOCDDeviceLoader
from pyetta.parsers import UnityParser
from pyetta.reporters import JUnitXmlReporter, ExitCodeReporter


@click.command("lnull", help="Dummy loader used in place where no loader is required.",
               cls=PyettaCommand, category='Loaders',
               plugin_name="_builtins")
def lnull() -> ExecutionCallable:
    class NullLoader(Loader):
        def load_to_device(self, progress: Optional[Callable[[int], None]] = None) -> None:
            if progress is not None:
                progress(100)

        def reset_device(self) -> None:
            pass

        def start_program(self):
            pass

    @execution_config
    def configure_pipeline(_: Context,
                           pipeline: ExecutionPipeline) -> None:
        pipeline.loader = NullLoader()

    return configure_pipeline


@click.command("cfile", cls=PyettaCommand, category='Collectors',
               plugin_name="_builtins",
               help="Collector that uses output from a text based file. File is opened as binary.")
@click.option("--file", help="Path to the file with captured output.",
              type=click.Path(exists=True, path_type=Path, dir_okay=False),
              required=True)
def cfile(file: Path) -> ExecutionCallable:
    @execution_config
    def configure_pipeline(context: Context,
                           pipeline: ExecutionPipeline) -> None:
        file_obj = IOBaseCollector(io.open(file=file, mode="rb"))
        pipeline.collector = file_obj
        context.with_resource(file_obj)

    return configure_pipeline


@click.command("lpyocd", cls=PyettaCommand, category='Loaders', plugin_name='_builtins',
               short_help="Loader for PyOCD.")
@click.option("--firmware", help="Path to the input test runner firmware.",
              type=click.Path(exists=True, path_type=Path), required=True)
@click.option("--probe", help="ID of the probe to use", required=False,
              type=str, metavar="PROBE_ID")
@click.option("--target",
              help="Chip target, must match the target connected to the host",
              required=False, type=str, metavar="TARGET_MCU")
def lpyocd(firmware: Path, target: Optional[str] = None,
           probe: Optional[str] = None) -> ExecutionCallable:
    """Loader for PyOCD.

    Note for this loader to work, PyOCD must be loaded with the correct boards
    and debuggers."""

    @execution_config
    def configure_pipeline(context: Context,
                           pipeline: ExecutionPipeline) -> None:
        loader = PyOCDDeviceLoader(target=target, probe=probe,
                                   firmware_path=firmware)
        pipeline.loader = loader
        context.with_resource(loader)

    return configure_pipeline


@click.command("cserial", cls=PyettaCommand, category='Collectors', plugin_name='_builtins',
               help="Collector that opens a serial port to collect data.")
@click.option("--baud", help="Baud rate of serial port.", default=115200,
              required=False, type=int, metavar="BAUD")
@click.option("--port", help="The serial port to use.",
              type=str, required=True, metavar="PORT")
def cserial(port: str, baud: int = 115200) -> ExecutionCallable:
    @execution_config
    def configure_pipeline(context: Context,
                           pipeline: ExecutionPipeline) -> None:
        serial = IOBaseCollector(Serial(port=port, baudrate=baud, timeout=5))
        pipeline.collector = serial
        context.with_resource(serial)

    return configure_pipeline


@click.command("punity", cls=PyettaCommand, category="Parsers", plugin_name="_builtins",
               help="Parser for the Unity unit test framework.")
@click.option("--name", help="optional name of this test suite",
              type=str, metavar="TEST_SUITE_NAME")
@click.option("-e", "--encoding", help="file encoding to open the file with.",
              default='ascii')
def punity(name: Optional[str] = None, encoding: str = 'ascii') -> ExecutionCallable:
    @execution_config
    def configure_pipeline(_: Context,
                           pipeline: ExecutionPipeline) -> None:
        parser = UnityParser(name, encoding)
        pipeline.parser = parser

    return configure_pipeline


@click.command("rjunitxml", cls=PyettaCommand, category="Reporters", plugin_name="_builtins",
               help="JUnit XML output reporter.")
@click.option("--file", "file_path", help="Output file path.", required=True,
              type=click.Path(path_type=Path))
@click.option("--fail-on-skipped", "fail_skipped",
              help="Returns a failure exit code if any tests are skipped.",
              is_flag=True, default=False, type=bool)
@click.option("--fail-on-empty", "fail_empty",
              help="Returns a failure exit code if no tests were detected.",
              is_flag=True, default=False, type=bool)
def rjunitxml(file_path: Path, fail_skipped: bool = False,
              fail_empty: bool = False) -> ExecutionCallable:
    @execution_config
    def configure_pipeline(_: Context,
                           pipeline: ExecutionPipeline) -> None:
        reporter = JUnitXmlReporter(file_path=file_path,
                                    fail_on_skipped=fail_skipped,
                                    fail_on_empty=fail_empty)
        pipeline.reporters.append(reporter)

    return configure_pipeline


@click.command("rexit", cls=PyettaCommand, category="Reporters", plugin_name="_builtins",
               help="Reporter to just output exit code.")
@click.option("--fail-on-skipped", "fail_skipped",
              help="Returns a failure exit code if any tests are skipped.",
              is_flag=True, default=False, type=bool)
@click.option("--fail-on-empty", "fail_empty",
              help="Returns a failure exit code if no tests were detected.",
              is_flag=True, default=False, type=bool)
def rexit(fail_skipped: bool = False, fail_empty: bool = False) -> ExecutionCallable:
    @execution_config
    def configure_pipeline(_: Context,
                           pipeline: ExecutionPipeline) -> None:
        reporter = ExitCodeReporter(fail_on_skipped=fail_skipped,
                                    fail_on_empty=fail_empty)
        pipeline.reporters.append(reporter)

    return configure_pipeline


def load_plugin():
    add_command_to_cli(lnull)
    add_command_to_cli(lpyocd)
    add_command_to_cli(cfile)
    add_command_to_cli(cserial)
    add_command_to_cli(punity)
    add_command_to_cli(rjunitxml)
    add_command_to_cli(rexit)
