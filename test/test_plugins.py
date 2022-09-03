from pathlib import Path

from click import Group
from click.testing import CliRunner


def test_load_plugins_via_extras_should_show_in_help(cli_entry: Group,
                                                     cli_runner: CliRunner,
                                                     examples_dir: Path):
    result = cli_runner.invoke(
        cli_entry,
        [
            f'--extras={examples_dir / "foo_plugin.py"}',
            '--help'
        ]
    )
    assert result.exit_code == 0
    assert 'lfoo' in result.output


def test_load_plugins_filtered_should_not_show_in_help(cli_entry: Group,
                                                       cli_runner: CliRunner,
                                                       examples_dir: Path):
    result = cli_runner.invoke(
        cli_entry,
        [
            '--exclude-plugins=foo_plugin',
            f'--extras={examples_dir / "foo_plugin.py"}',
            '--help'
        ]
    )

    assert result.exit_code == 0
    assert 'lfoo' not in result.output


def test_load_bad_plugin_returns_failed(cli_entry: Group,
                                        cli_runner: CliRunner,
                                        examples_dir: Path):

    result = cli_runner.invoke(
        cli_entry,
        [
            f'--extras={examples_dir / "assert_plugin.py"}',
        ]
    )

    assert result.exit_code != 0
