import importlib
from multiprocessing import Lock
from pathlib import Path
from typing import cast, List

from click import Group
from click.testing import CliRunner

import pyetta.cli.cli as pyetta_cli

from typing import Iterable
from xml.etree.ElementTree import fromstring, Element

import pytest

from junit_xml import TestSuite, TestCase
# ignoring junit_xml test classes, as they have nothing to do with unit testing
TestSuite.__test__ = False
TestCase.__test__ = False


@pytest.fixture()
def test_root() -> Path:
    return Path(__file__).parent.resolve()


@pytest.fixture()
def test_suites() -> Iterable[TestSuite]:
    test_suites = [
        TestSuite(name="test_suite_1",
                  test_cases=[
                      TestCase(name="test_1", file="/mypath/foo.c",
                               line=1, stdout="test one output"),
                      TestCase(name="test_2", file="/mypath/foo.c",
                               line=2, stdout="test two output"),
                      TestCase(name="test_3", file="/mypath/foo.c",
                               line=3, stdout="test three output"),
                  ]),
        TestSuite(name="test_suite_2",
                  test_cases=[
                      TestCase(name="test_a", file="/mypath/foo.c",
                               line=12, stdout="test aa output"),
                      TestCase(name="test_b", file="/mypath/foo.c",
                               line=23, stdout="test bbb output"),
                      TestCase(name="test_c", file="/mypath/foo.c",
                               line=34, stdout="test cccc output"),
                  ])
    ]

    return test_suites


@pytest.fixture()
def test_suites_xml() -> Element:
    raw_xml = """<?xml version="1.0" encoding="utf-8"?>
                <testsuites disabled="0" errors="0" failures="0" tests="6"
                time="0.0">
                    <testsuite disabled="0" errors="0" failures="0"
                    name="test_suite_1" skipped="0" tests="3" time="0">
                        <testcase name="test_1" file="/mypath/foo.c" line="1">
                            <system-out>test one output</system-out>
                        </testcase>
                        <testcase name="test_2" file="/mypath/foo.c" line="2">
                            <system-out>test two output</system-out>
                        </testcase>
                        <testcase name="test_3" file="/mypath/foo.c" line="3">
                            <system-out>test three output</system-out>
                        </testcase>
                    </testsuite>
                    <testsuite disabled="0" errors="0" failures="0"
                    name="test_suite_2" skipped="0" tests="3" time="0">
                        <testcase name="test_a" file="/mypath/foo.c" line="12">
                            <system-out>test aa output</system-out>
                        </testcase>
                        <testcase name="test_b" file="/mypath/foo.c" line="23">
                            <system-out>test bbb output</system-out>
                        </testcase>
                        <testcase name="test_c" file="/mypath/foo.c" line="34">
                            <system-out>test cccc output</system-out>
                        </testcase>
                    </testsuite>
                </testsuites>
    """

    elements = fromstring(raw_xml)

    for elem in elements.iter('*'):
        if elem.text is not None:
            elem.text = elem.text.strip()
        if elem.tail is not None:
            elem.tail = elem.tail.strip()

    return elements


@pytest.fixture()
def test_suite() -> Iterable[TestSuite]:
    test_suite = [
        TestSuite(name="test_suite_1",
                  test_cases=[
                      TestCase(name="test_1", file="/mypath/foo.c",
                               line=1, stdout="/mypath/foo.c:1:test_1:PASS"),
                      TestCase(name="test_2", file="/mypath/foo.c",
                               line=2, stdout="/mypath/foo.c:2:test_2:PASS"),
                      TestCase(name="test_3", file="/mypath/foo.c",
                               line=3, stdout="/mypath/foo.c:3:test_3:PASS"),
                  ])
    ]

    return test_suite


@pytest.fixture()
def test_suite_xml() -> Element:
    raw_xml = """<?xml version="1.0" encoding="utf-8"?>
                <testsuites disabled="0" errors="0" failures="0" tests="3"
                time="0.0">
                    <testsuite disabled="0" errors="0" failures="0"
                    name="test_suite_1" skipped="0" tests="3" time="0">
                        <testcase name="test_1" file="/mypath/foo.c" line="1">
                            <system-out>/mypath/foo.c:1:test_1:PASS</system-out>
                        </testcase>
                        <testcase name="test_2" file="/mypath/foo.c" line="2">
                            <system-out>/mypath/foo.c:2:test_2:PASS</system-out>
                        </testcase>
                        <testcase name="test_3" file="/mypath/foo.c" line="3">
                            <system-out>/mypath/foo.c:3:test_3:PASS</system-out>
                        </testcase>
                    </testsuite>
                </testsuites>
    """

    elements = fromstring(raw_xml)

    for elem in elements.iter('*'):
        if elem.text is not None:
            elem.text = elem.text.strip()
        if elem.tail is not None:
            elem.tail = elem.tail.strip()

    return elements


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
