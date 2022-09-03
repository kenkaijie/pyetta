"""Reporters are used to mutate the test suite outputs of the parsers
into various formats.
"""
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable, Optional

from junit_xml import TestSuite, TestCase, to_xml_report_file

log = logging.getLogger("pyetta.reporters")


class Reporter(ABC):
    """Base interface for a reporter.
    """

    @abstractmethod
    def generate_report(self, tests: Optional[Iterable[TestSuite]]) -> int:
        """Generates a report given an iterable of tests.

        :param tests: tests to generate the report from.
        :returns: a value indicating the error code to return.
        """
        ...

    @staticmethod
    def generate_exit_code(test_suites: Iterable[TestSuite], fail_empty: bool,
                           fail_skipped: bool) -> int:
        """Inspects test suites to determine the best exit code to return.

        :param test_suites: The test suites to check over.
        :param fail_empty: Set to true if we want empty tests to be considered as a fail.
        :param fail_skipped: Set to true if we want to consider skipped test as a fail.

        :returns: the number of failed tests.
        """
        test_count = 0
        test_fails = 0
        for test_suite in test_suites:
            for test_case in test_suite.test_cases:  # type: TestCase
                test_count += 1
                if test_case.is_error() or test_case.is_failure():
                    test_fails += 1
                if fail_skipped and test_case.is_skipped():
                    test_fails += 1
        if fail_empty and test_count == 0:
            test_fails += 1
        return test_fails


class ExitCodeReporter(Reporter):
    def __init__(self, fail_on_skipped: bool = False,
                 fail_on_empty: bool = False) -> None:
        """Simple reporter that just modifies the exit code. It returns a simple 1 or 0 depending
        on if there are passed or failed tests.

        :param fail_on_skipped: Set to true if skipped tests should count as failures.
        :param fail_on_empty: Set to true if the lack of any tests cases results in a failure.
        """
        self._fail_on_skipped = fail_on_skipped
        self._fail_on_empty = fail_on_empty
        super().__init__()

    def generate_report(self, tests: Optional[Iterable[TestSuite]]) -> int:
        exit_code = self.generate_exit_code(tests, fail_skipped=self._fail_on_skipped,
                                            fail_empty=self._fail_on_empty)
        return min(exit_code, 1)


class JUnitXmlReporter(ExitCodeReporter):

    def __init__(self, file_path: Path,
                 fail_on_skipped: bool = False,
                 fail_on_empty: bool = False) -> None:
        """JUnit XML style reporter. Produces JUnit XML documentation that can be parsed by
        consumers which support this format.

        :param file_path: The output file to write the xml contents to.
        :param fail_on_skipped: Set to true if skipped tests should count as failures.
        :param fail_on_empty: Set to true if the lack of any tests cases results in a failure.
        """
        self._output_filepath = file_path
        self._fail_on_skipped = fail_on_skipped
        self._fail_on_empty = fail_on_empty
        super().__init__()

    def generate_report(self, tests: Optional[Iterable[TestSuite]]) -> int:
        log.debug(
            f"Generating JUnit XML log for tests at f{self._output_filepath}.")
        with open(self._output_filepath, 'w') as fo:
            to_xml_report_file(fo, test_suites=tests, encoding='utf-8')

        return super().generate_report(tests)
