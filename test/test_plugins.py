import shutil
from pathlib import Path

import pytest
from click.testing import CliRunner

from pyetta.cli.cli import cli


@pytest.fixture()
def examples_dir(tmp_path) -> Path:
    """Creates and copies the plugin samples folder into a temp directory.
    """
    real_examples_dir = Path(__file__).parent.joinpath("../examples").resolve()
    files = [real_examples_dir.joinpath(f).resolve()
             for f in real_examples_dir.iterdir()
             if f.is_file()]

    for file in files:
        shutil.copy2(file, tmp_path / file.name)

    return tmp_path


def test_load_plugins_via_extras_should_show_in_help(examples_dir: Path):
    runner = CliRunner()
    result = runner.invoke(cli,
                           [f'--extras={examples_dir / "foo_plugin.py"}',
                            '--help'])
    assert result.exit_code == 0
    assert 'lfoo' in result.output
