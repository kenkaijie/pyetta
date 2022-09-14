import importlib
from multiprocessing import Lock
from pathlib import Path
from typing import cast, List

from click import Group
from click.testing import CliRunner

import pyetta.cli.cli as pyetta_cli

import pytest


@pytest.fixture()
def test_root() -> Path:
    return Path(__file__).parent.resolve()


@pytest.fixture(scope="module")
def serialise_lock() -> Lock:
    """Just a lock to ensure all cli tests run synchronously."""
    return Lock()


@pytest.fixture()
def examples_dir(test_root: Path) -> Path:
    """Points to the examples directory.
    """
    return (test_root / "../examples").resolve()


@pytest.fixture(autouse=True)
def unload_plugins() -> None:
    """Used for reloading the plugins module between tests.
    """
    importlib.reload(pyetta_cli)


@pytest.fixture
def cli_runner(serialise_lock, tmp_path) -> CliRunner:
    runner = CliRunner()
    with serialise_lock:
        with runner.isolated_filesystem(tmp_path):
            yield runner


@pytest.fixture
def cli_entry() -> Group:
    return cast(Group, pyetta_cli.cli)


@pytest.fixture()
def builtins_filepath(test_root: Path) -> Path:
    return (test_root / "../pyetta/_builtins.py").resolve()


@pytest.fixture()
def builtins_args(builtins_filepath) -> List[str]:
    return [f'--extras={builtins_filepath}']
