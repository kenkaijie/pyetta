from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

import click
from click import Context, HelpFormatter
from pyetta.loaders.interfaces import IDeviceLoader


@dataclass
class ExecutionResources:
    loader: Optional[IDeviceLoader] = None


class CategorisedCommand(click.Command):

    def __init__(self, category: str = "Commands", *args, **kwargs):
        self.category = category
        super(CategorisedCommand, self).__init__(*args, **kwargs)


class CategorisedHelp(click.Group):

    def format_commands(self, ctx: Context, formatter: HelpFormatter):
        command_labels: Dict[str, List[Tuple[str, str]]] = {}

        for subcommand in self.list_commands(ctx):
            cmd = self.get_command(ctx, subcommand)
            if cmd is None:
                continue

            label = getattr(cmd, 'category', 'Commands')
            help = cmd.help or ''

            if label not in command_labels:
                command_labels[label] = []

            command_labels[label].append((subcommand, help))

        for label, subcommands in command_labels.items():
            with formatter.section(label):
                formatter.write_dl(subcommands)


def root_context(context: Context) -> Context:
    parent = context
    while parent.parent is not None:
        parent = parent.parent
    return parent
