"""Example plugin file that asserts an exception whe loading.
"""


def load_plugin():
    """Magic method to load the plugin to the system. This is called by the CLI
    prior to invoking any command."""
    raise RuntimeError("This plugin always asserts!")
