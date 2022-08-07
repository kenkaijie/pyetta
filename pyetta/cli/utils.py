from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Dict, List, Tuple, Optional, Any, Sequence, Union, Callable, Set

import click
from click import Context, HelpFormatter, Command

from pyetta.loaders.interfaces import IDeviceLoader


@dataclass
class CliState:
    """ CLI shared state.
    """
    extras: Optional[Path] = None
    plugins_filter: Optional[Set[str]] = None
    loader: Optional[IDeviceLoader] = None


class PyettaCommand(click.Command):
    """Command base for pyetta commands, use this as your class injection for click commands.

    This uses the category property to allow proper help text to group the command types.
    """

    def __init__(self, category: str = "Commands", plugin_name: Optional[str] = None, *args, **kwargs):
        self.category = category
        self.plugin_name = plugin_name
        super(PyettaCommand, self).__init__(*args, **kwargs)


class PyettaGroup(click.Group):
    """The base pyetta click grouping.

    Provides custom help text which includes both command.
    """

    def __init__(self,
                 name: Optional[str] = None,
                 commands: Optional[Union[Dict[str, Command], Sequence[Command]]] = None,
                 pre_invoke_handler: Optional[Callable[[click.Group, Context], None]] = None,
                 **attrs: Any) -> None:
        """
        :param name: The name of the group.
        :param commands: The commands belonging to this group.
        :param pre_invoke_handler: A handler that is called just before the invocation of the command, but after the
                                   argument parsing.
        """
        self._pre_invoke_handler = pre_invoke_handler
        super(PyettaGroup, self).__init__(name=name, commands=commands, **attrs)

    def invoke(self, ctx: Context) -> Any:
        if self._pre_invoke_handler is not None and callable(self._pre_invoke_handler):
            self._pre_invoke_handler(self, ctx)
        return super().invoke(ctx)

    def format_commands(self, ctx: Context, formatter: HelpFormatter):
        command_labels: Dict[str, List[Tuple[str, str]]] = {}

        for subcommand in self.list_commands(ctx):
            cmd = self.get_command(ctx, subcommand)
            if cmd is None:
                continue

            label = getattr(cmd, 'category', 'Commands')
            plugin_name = getattr(cmd, 'plugin_name', None)
            help_str = cmd.help or ''
            help_str += f" [plugin: {plugin_name}]" if plugin_name is not None else ''

            if label not in command_labels:
                command_labels[label] = []

            command_labels[label].append((subcommand, help_str))

        for label, subcommands in command_labels.items():
            with formatter.section(label):
                formatter.write_dl(subcommands)




