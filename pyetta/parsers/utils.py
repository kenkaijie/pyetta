from typing import Iterable

from junit_xml import TestSuite, TestCase


def result_from_test_suites(test_suites: Iterable[TestSuite]) -> int:
    for test_suite in test_suites:
        for test_case in test_suite.test_cases:  # type: TestCase
            if test_case.is_error() or test_case.is_failure() or test_case.is_skipped():
                return 1
    return 0
