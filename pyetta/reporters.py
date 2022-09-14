"""Reporters are used to mutate the test suite outputs of the parsers
into various formats.
"""
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable, Optional, Dict

import pyetta.parser_data as p
import junit_xml as j

log = logging.getLogger("pyetta.reporters")


class Reporter(ABC):
    """Base interface for a reporter.
    """

    @abstractmethod
    def generate_report(self, test_cases: Iterable[p.TestCase]) -> int:
        """Generates a report given an iterable of tests.

        :param test_cases: tests to generate the report from.
        :returns: a value indicating the error code to return.
        """

    @staticmethod
    def generate_exit_code(test_cases: Iterable[p.TestCase], fail_empty: bool,
                           fail_skipped: bool) -> int:
        """Inspects test suites to determine the best exit code to return.

        :param test_cases: The test suites to check over.
        :param fail_empty: Set to true if we want empty tests to be considered as a fail.
        :param fail_skipped: Set to true if we want to consider skipped test as a fail.

        :returns: the number of failed tests.
        """
        test_count = 0
        test_fails = 0
        for test_case in test_cases:  # type: p.TestCase
            test_count += 1
            if test_case.result == p.TestResult.Fail:
                test_fails += 1
            if fail_skipped and test_case.result == p.TestResult.Skip:
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

    def generate_report(self, tests: Iterable[p.TestCase]) -> int:
        exit_code = self.generate_exit_code(tests,
                                            fail_skipped=self._fail_on_skipped,
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

    @staticmethod
    def _to_junit_xml(test_cases: Iterable[p.TestCase]) -> Iterable[j.TestSuite]:
        # to convert to a junit scheme, we group them by test group
        junit_test_suites: Dict[str, j.TestSuite] = dict()
        for test_case in test_cases:
            if test_case.group not in junit_test_suites:
                junit_test_suites[test_case.group] = j.TestSuite(name=test_case.group)
            junit_test_case = j.TestCase(name=test_case.name,
                                         stdout=test_case.stdout,
                                         stderr=test_case.stderr,
                                         timestamp=test_case.timestamp_s,
                                         line=test_case.line_num,
                                         file=test_case.filepath)
            junit_test_suites[test_case.group].test_cases.append(junit_test_case)

        return [test_suite for test_suite in junit_test_suites.values()]

    def generate_report(self, test_cases: Optional[Iterable[p.TestCase]]) -> int:
        log.debug("Generating JUnit XML log for tests at %s.", self._output_filepath)
        junit_tests = self._to_junit_xml(test_cases)
        with open(self._output_filepath, 'w') as fo:
            j.to_xml_report_file(fo, test_suites=junit_tests, encoding='utf-8')

        return super().generate_report(test_cases)
