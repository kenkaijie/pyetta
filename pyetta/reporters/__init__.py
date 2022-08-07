"""Reporters are used to mutate the test suite outputs of the parsers
into various formats.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable, Optional

from junit_xml import TestSuite

class Reporter(ABC):
    """Base interface for a reporter
    """

    @abstractmethod
    def generate_report(tests: Optional[Iterable[TestSuite]]) -> int:
        """Generates a report given a iterable of tests.
        
        :param tests: tests to generate the report from.
        :returns: a value indicating the error code to return
        """
        pass

class JUnitXmlReporter(Reporter):

    def __init__(self, file_path: Optional[Path] = None,
        skipped_as_error: bool = False) -> None:
        super().__init__()

    def generate_report(tests: Optional[Iterable[TestSuite]]) -> int:
        with open(junit, 'w') as fo:
            to_xml_report_file(fo, test_suites=test_suites, encoding='utf-8')
