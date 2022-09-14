import uuid
from pathlib import Path
from typing import List

import pytest
from click import Group
from click.testing import CliRunner


@pytest.fixture()
def sample_file_all_pass(tmp_path) -> Path:
    filepath = tmp_path / f"{uuid.uuid4()}.py"
    with open(filepath, "w") as fi:
        fi.write("""
/mypath/foo.c:1:test_1:PASS
/mypath/foo.c:2:test_2:PASS
/mypath/foo.c:3:test_3:PASS

-----------------------
3 Tests 0 Failures 0 Ignored
OK
""")
    yield filepath


@pytest.fixture()
def sample_file_ignores(tmp_path) -> Path:
    filepath = tmp_path / f"{uuid.uuid4()}.py"
    with open(filepath, "w") as fi:
        fi.write("""
/mypath/foo.c:1:test_1:PASS
/mypath/foo.c:2:test_2:IGNORE
/mypath/foo.c:3:test_3:PASS

-----------------------
3 Tests 0 Failures 1 Ignored
OK
""")
    yield filepath


def test_cli_should_load_builtins(builtins_args: List[str],
                                  cli_runner: CliRunner,
                                  cli_entry: Group):
    builtins_args.extend([
        '--help'
    ])

    result = cli_runner.invoke(cli_entry, builtins_args)

    assert result.exit_code == 0


def test_null_stages_should_return_correct_output(sample_file_all_pass: Path,
                                                  builtins_args: List[str],
                                                  cli_runner: CliRunner,
                                                  cli_entry: Group,
                                                  tmp_path: Path):

    builtins_args.extend([
        'lnull',
        'cfile',
        f'--file={sample_file_all_pass}',
        'punity',
        '--name=test_suite_1',
        'rexit',
        '--fail-on-empty'
    ])

    result = cli_runner.invoke(cli_entry, builtins_args)

    assert result.exit_code == 0


def test_ignored_tests_should_return_fail(sample_file_ignores: Path,
                                          builtins_args: List[str],
                                          cli_runner: CliRunner,
                                          cli_entry: Group,
                                          tmp_path: Path):

    builtins_args.extend([
        'lnull',
        'cfile',
        f'--file={sample_file_ignores}',
        'punity',
        '--name=test_suite_1',
        'rexit',
        '--fail-on-empty',
        '--fail-on-skipped'
    ])

    result = cli_runner.invoke(cli_entry, builtins_args)

    assert result.exit_code != 0
