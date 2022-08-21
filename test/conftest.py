from typing import Iterable
from xml.etree.ElementTree import fromstring, Element

import pytest
from junit_xml import TestSuite, TestCase

# ignoring junit_xml test classes, as they have nothing to do with unit testing
TestSuite.__test__ = False
TestCase.__test__ = False


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
