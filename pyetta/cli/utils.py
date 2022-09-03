import inspect
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Sequence, Union, Callable, \
    Set

import click
from click import Context, HelpFormatter, Command

from pyetta.collectors import Collector
from pyetta.loaders import Loader
from pyetta.parsers import Parser
from pyetta.reporters import Reporter

log = logging.getLogger("pyetta.cli")


@dataclass
class CliState:
    """ CLI shared state.
    """
    extras: Set[Path] = field(default_factory=set)
    plugins_filter: Set[str] = field(default_factory=set)


@dataclass
class ExecutionPipeline:
    """The default execution pipeline, this takes encodes the algorithm used to
    flash and load a system.
    """
    loader: Loader = None
    collector: Collector = None
    parser: Parser = None
    reporters: List[Reporter] = field(default_factory=list)

    def is_valid(self) -> bool:
        return self.loader is not None and \
               self.collector is not None and \
               self.parser is not None and \
               len(self.reporters) > 0

    def __setattr__(self, key: str, value: Any) -> None:
        if key == "loader" and self.loader is not None:
            raise ValueError("The CLI only supports a single loader. "
                             f"Current loader: {self.loader}")
        elif key == "collector" and self.collector is not None:
            raise ValueError("The CLI only supports a single collector. "
                             f"Current collector: {self.collector}.")
        elif key == "parser" and self.parser is not None:
            raise ValueError("The CLI only supports a single parser. "
                             f"Current parser: {self.parser}.")
        super(ExecutionPipeline, self).__setattr__(key, value)


ExecutionCallable = Callable[[Context, ExecutionPipeline], None]
"""Function signature for execution callables.
"""

# we only get the items that subclass Exception, we will invisibly pass through
# BaseException items as they are program stopping exceptions.
__click_exception_types = tuple(
    obj for _, obj in inspect.getmembers(click.exceptions)
    if inspect.isclass(obj) and issubclass(obj, Exception))


def execution_config(func: ExecutionCallable) -> ExecutionCallable:
    """General decorator for the items that go into an execution plan. Encodes
    click exceptions to ensure that the proper logging information is hidden.
    """

    def execution_function(context: Context,
                           pipeline: ExecutionPipeline) -> None:
        try:
            func(context, pipeline)
        except (EOFError, KeyboardInterrupt) + __click_exception_types as ec:
            # re-raise, click has official support for these exceptions, and
            # should pass through
            log.debug("Exception caught while running the execution plan.",
                      exc_info=ec)
            raise ec
        except Exception as ec:
            log.debug("Exception caught while running the execution plan.",
                      exc_info=ec)
            raise click.ClickException(str(ec)) from ec

    return execution_function


class PyettaCommand(click.Command):
    """Command base for pyetta commands, use this as your class injection for
    click commands.

    This uses the category property to allow proper help text to group the
    command types.
    """

    def __init__(self, category: str = "Commands",
                 plugin_name: Optional[str] = None, *args, **kwargs):
        """

        :param category: The category this plugin belongs to. This shows up in the help page.
        :param plugin_name: Name given to the plugin loading this command. Used in the help
                            function to help with filtering.
        """
        self.category = category
        self.plugin_name = plugin_name
        super(PyettaCommand, self).__init__(*args, **kwargs)


class PyettaCLIRoot(click.Group):
    """The base pyetta click grouping for subcommands of the cli. Has some
    "special" hooks to ensure plugins are loaded and the appropriate times.

    Provides custom help text which includes both command.
    """

    def __init__(self,
                 name: Optional[str] = None,
                 commands: Optional[
                     Union[Dict[str, Command], Sequence[Command]]] = None,
                 plugin_handler: Optional[
                     Callable[[click.Group, Context], None]] = None,
                 **attrs: Any) -> None:
        """
        :param name: The name of the group.
        :param commands: The commands belonging to this group.
        :param plugin_handler: A handler that is called just before the
                               invocation of the command, but after the
                               argument parsing.
        """
        if plugin_handler is not None and not callable(plugin_handler):
            raise TypeError("plugin_handler must be a callable!")
        self._plugin_handler = plugin_handler
        self._plugins_loaded = False
        super(PyettaCLIRoot, self).__init__(name=name, commands=commands,
                                            **attrs)

    def _call_plugins_loaded_once(self, ctx: Context) -> None:
        """Little tool to ensure the loading of plugins only happens once. This
        is supposed to be handled as late as possible.

        For click, this is either just before invoking the command, or if the
        help is called, it will load the plugins before invoking help (to
        ensure the help can show the new commands).
        """
        if not self._plugins_loaded:
            self._plugins_loaded = True
            self._plugin_handler(self, ctx)

    def get_help(self, ctx: Context) -> str:
        self._call_plugins_loaded_once(ctx)
        return super(PyettaCLIRoot, self).get_help(ctx)

    def invoke(self, ctx: Context) -> Any:
        self._call_plugins_loaded_once(ctx)
        return super().invoke(ctx)

    def format_commands(self, ctx: Context, formatter: HelpFormatter):
        command_labels: Dict[str, List[Tuple[str, str]]] = {}

        for subcommand in self.list_commands(ctx):
            cmd = self.get_command(ctx, subcommand)
            if cmd is None:
                continue

            label = getattr(cmd, 'category', 'Commands')
            plugin_name = getattr(cmd, 'plugin_name', None)
            help_str = cmd.short_help or cmd.help or ''
            if plugin_name is not None:
                help_str += f" [plugin: {plugin_name}]"

            if label not in command_labels:
                command_labels[label] = []

            command_labels[label].append((subcommand, help_str))

        for label, subcommands in command_labels.items():
            with formatter.section(label):
                formatter.write_dl(subcommands)
