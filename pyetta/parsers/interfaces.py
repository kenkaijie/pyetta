from abc import ABC, abstractmethod
from typing import List, Optional, Iterable

from junit_xml import TestSuite


class Parser(ABC):
    """Pyetta's parser stage.

    The parser stage is fed the input from a collector in the form of bytes.
    """
    @abstractmethod
    def feed_data(self, data_chunk: bytes) -> Optional[List[TestSuite]]:
        """Feeds a data chunk to the parser.

        :param data_chunk: A chunk of data to parse. This chunk should be complete it itself.

        :returns: A list of parsed test suites, or None if parsing is in progress.
        """
        pass

    @abstractmethod
    def abort(self) -> None:
        """Aborts the parser. Called by the executor when the collection is stopped. 
        
        If stopped before parse completion, the parser should add a failed test to the test suite.
        """
        pass

    @property
    @abstractmethod
    def test_suites(self) -> Optional[List[TestSuite]]:
        """The parsed test suites. This should be the same as the return calue from
        :ref:feed_data.
        
        :returns: A list of parsed test suites, or None if parsing is in progress.
        """
        pass

    @staticmethod
    def generate_exit_code(test_suites: Iterable[TestSuite], 
                           fail_empty: bool, fail_skipped: bool) -> int:
        """Inspects test suites to determine the best exit code to return.
        
        :param test_suites: The test suites to check over.

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
