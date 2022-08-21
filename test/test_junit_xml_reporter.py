import uuid
from pathlib import Path
from typing import Iterable
from xml.etree.ElementTree import parse, XMLParser, tostring, Element

from junit_xml import TestSuite

from pyetta.reporters import JUnitXmlReporter


def test_should_output_correct_xml_format(tmp_path: Path,
                                          test_suites: Iterable[TestSuite],
                                          test_suites_xml: Element):
    xml_output_file = tmp_path / f"{uuid.uuid4()}.xml"
    reporter = JUnitXmlReporter(xml_output_file)

    reporter.generate_report(test_suites)

    actual_xml = parse(xml_output_file, XMLParser()).getroot()

    # strip all non empty fields
    for elem in actual_xml.iter('*'):
        if elem.text is not None:
            elem.text = elem.text.strip()
        if elem.tail is not None:
            elem.tail = elem.tail.strip()

    assert tostring(actual_xml) == tostring(test_suites_xml)
