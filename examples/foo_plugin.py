"""Example plugin file, this is how to structure a file to inject extensions
into the pyetta cli.

Some comments are peppered around this file for demonstrating the features. For
more information, see the documentation.
"""
import click
from click import Context

from pyetta.cli.cli import add_command_to_cli
from pyetta.cli.utils import PyettaCommand, ExecutionCallable, \
    execution_config, ExecutionPipeline
from pyetta.loaders import Loader


@click.command("lfoo",
               help="Loader for el pepe",
               cls=PyettaCommand, category='Loaders',
               plugin_name="foo_plugin")
def lfoo() -> ExecutionCallable:
    """Custom click based cli command. This will be added dynamically at
    runtime but can take any options typical to the cli.

    Given the pipeline architecture, ensure this returns a callable that
    registers the component to the pipeline stage."""

    @execution_config
    def configure_pipeline(_: Context,
                           pipeline: ExecutionPipeline) -> None:
        click.echo("Running the foo loader!")
        pipeline.loader = Loader()

        # if the resource to register is a context manager, use click's
        # context.with_resource() function to register and load it.

    return configure_pipeline


def load_plugin():
    """Magic method to load the plugin to the system. This is called by the CLI
    prior to invoking any command."""
    add_command_to_cli(lfoo)
