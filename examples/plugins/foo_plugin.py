"""Example plugin file, this is
"""
import click
from click import pass_context, Context

from pyetta.cli.cli import add_command_to_cli
from pyetta.cli.utils import PyettaCommand


@click.command("lfoo",
               help="Loader for el pepe",
               cls=PyettaCommand, category='Loaders',
               plugin_name="foo_plugin")
@pass_context
def lfoo(context: Context):
    click.echo("Running the foo loader!")


def load_plugin():
    add_command_to_cli(lfoo)
