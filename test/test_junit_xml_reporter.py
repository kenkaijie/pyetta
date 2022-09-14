import uuid
from pathlib import Path
from typing import Iterable
from xml.etree.ElementTree import parse, XMLParser, tostring, Element, fromstring

import pytest
from pyetta.parser_data import TestCase, TestResult

from pyetta.reporters import JUnitXmlReporter


@pytest.fixture()
def test_cases() -> Iterable[TestCase]:
    test_cases = [
        TestCase(group="test_suite_1",
                 name="test_1",
                 result=TestResult.Pass,
                 filepath="/mypath/foo.c",
                 line_num=1,
                 stdout="/mypath/foo.c:1:test_1:PASS"),
        TestCase(group="test_suite_1",
                 name="test_2",
                 result=TestResult.Pass,
                 filepath="/mypath/foo.c",
                 line_num=2,
                 stdout="/mypath/foo.c:2:test_2:PASS"),
        TestCase(group="test_suite_1",
                 name="test_3",
                 result=TestResult.Pass,
                 filepath="/mypath/foo.c",
                 line_num=3,
                 stdout="/mypath/foo.c:3:test_3:PASS"),
    ]

    return test_cases


@pytest.fixture()
def test_cases_xml() -> Element:
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


def test_should_output_correct_xml_format(tmp_path: Path,
                                          test_cases: Iterable[TestCase],
                                          test_cases_xml: Element):
    xml_output_file = tmp_path / f"{uuid.uuid4()}.xml"
    reporter = JUnitXmlReporter(xml_output_file)

    reporter.generate_report(test_cases)

    actual_xml = parse(xml_output_file, XMLParser()).getroot()

    # strip all non empty fields
    for elem in actual_xml.iter('*'):
        if elem.text is not None:
            elem.text = elem.text.strip()
        if elem.tail is not None:
            elem.tail = elem.tail.strip()

    assert tostring(actual_xml) == tostring(test_cases_xml)
