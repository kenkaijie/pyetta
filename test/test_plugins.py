import importlib
import shutil
from pathlib import Path

import pytest
from click.testing import CliRunner

# this must be imported as a module
import pyetta.cli.cli as pyetta_cli


@pytest.fixture()
def tmp_examples_dir(tmp_path) -> Path:
    """Creates and copies the plugin samples folder into a temp directory.
    """
    real_examples_dir = Path(__file__).parent.joinpath("../examples").resolve()
    files = [real_examples_dir.joinpath(f).resolve()
             for f in real_examples_dir.iterdir()
             if f.is_file()]

    for file in files:
        shutil.copy2(file, tmp_path / file.name)

    return tmp_path


@pytest.fixture(autouse=True)
def unload_plugins() -> None:
    """Used for reloading the plugins module between tests.
    """
    importlib.reload(pyetta_cli)


@pytest.fixture
def cli_runner(tmp_examples_dir) -> CliRunner:
    runner = CliRunner()
    with runner.isolated_filesystem(tmp_examples_dir):
        yield runner


def test_load_plugins_via_extras_should_show_in_help(cli_runner: CliRunner,
                                                     tmp_examples_dir: Path):
    result = cli_runner.invoke(
        pyetta_cli.cli,
        [f'--extras={tmp_examples_dir / "foo_plugin.py"}',
         '--help'])
    assert result.exit_code == 0
    assert 'lfoo' in result.output


def test_load_plugins_filtered_should_not_show_in_help(cli_runner: CliRunner,
                                                       tmp_examples_dir: Path):
    result = cli_runner.invoke(
        pyetta_cli.cli,
        ['--exclude-plugins=foo_plugin',
         f'--extras={tmp_examples_dir / "foo_plugin.py"}',
         '--help'])
    assert result.exit_code == 0
    assert 'lfoo' not in result.output
