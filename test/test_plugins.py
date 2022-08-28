import importlib
from pathlib import Path

import pytest
from click.testing import CliRunner

# this must be imported as a module
import pyetta.cli.cli as pyetta_cli
from threading import Lock


@pytest.fixture(scope="module")
def serialise_lock() -> Lock:
    """Just a lock to ensure all cli tests run synchronously."""
    return Lock()


@pytest.fixture()
def examples_dir(tmp_path) -> Path:
    """Creates and copies the plugin samples folder into a temp directory.
    """
    return Path(__file__).parent.joinpath("../examples").resolve()


@pytest.fixture(autouse=True)
def unload_plugins() -> None:
    """Used for reloading the plugins module between tests.
    """
    importlib.reload(pyetta_cli)


@pytest.fixture
def cli_runner(serialise_lock) -> CliRunner:
    runner = CliRunner()
    with serialise_lock:
        yield runner


def test_load_plugins_via_extras_should_show_in_help(cli_runner: CliRunner,
                                                     examples_dir: Path):
    result = cli_runner.invoke(
        pyetta_cli.cli,
        [f'--extras={examples_dir / "foo_plugin.py"}',
         '--help'])
    assert result.exit_code == 0
    assert 'lfoo' in result.output


def test_load_plugins_filtered_should_not_show_in_help(cli_runner: CliRunner,
                                                       examples_dir: Path):
    result = cli_runner.invoke(
        pyetta_cli.cli,
        ['--exclude-plugins=foo_plugin',
         f'--extras={examples_dir / "foo_plugin.py"}',
         '--help'])
    assert result.exit_code == 0
    assert 'lfoo' not in result.output
