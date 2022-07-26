from typing import Iterable

from junit_xml import TestSuite, TestCase


def result_from_test_suites(test_suites: Iterable[TestSuite],
                            fail_empty: bool, fail_skipped: bool) -> int:
    test_count = 0
    for test_suite in test_suites:
        for test_case in test_suite.test_cases:  # type: TestCase
            test_count += 1
            if test_case.is_error() or test_case.is_failure():
                return 1
            if fail_skipped and test_case.is_skipped():
                return 1
    if fail_empty and test_count == 0:
        return 1
    return 0
