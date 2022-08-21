import logging
import re
from abc import ABC, abstractmethod
from enum import IntEnum
from typing import Optional, List, Dict

from junit_xml import TestCase, TestSuite

log = logging.getLogger('pyetta.parsers')


class Parser(ABC):
    """Pyetta parser stage-

    The parser stage is fed the input from a collector in the form of bytes.
    """

    RESERVED_TEST_SUITE = "pyetta.parser"

    def __init__(self):
        self._test_suites: Dict[str, TestSuite] = {}

    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @abstractmethod
    def feed_data(self, data_chunk: bytes) -> None:
        """Feeds a data chunk to the parser.

        :param data_chunk: A chunk of data to parse. This chunk should be
                           complete it itself.
        """
        pass

    @abstractmethod
    def stop(self, forced: bool = False) -> None:
        """Stops the parser and forces a completion. Called by the executor
        when the collection is stopped.

        :param forced: Set to true to stop due to an error.

        If stopped before parse completion the parser must add a failed test
        indicating a forced stopped.
        """
        pass

    @property
    @abstractmethod
    def done(self) -> bool:
        """Gets whether the parser is done or no.

        :returns: True is parser is done (parser errors are communicated via
                  the test suites).
        """

    @property
    @abstractmethod
    def test_suites(self) -> Optional[List[TestSuite]]:
        """The parsed test suites up to this point. Note this may be incomplete
        if called before the parser is stopped.

        :returns: A list of parsed test suites.
        """
        pass

    def _add_parser_error(self, message: Optional[str] = None) -> None:
        """Generates an error test case and stores it under the reserved
        special test suite.

        :param message: Optional message to place in the error.
        """

        test_case = TestCase("parser_error", "pyetta.parsers", line=0)
        test_case.add_error_info(message or "parser error")
        if Parser.RESERVED_TEST_SUITE not in self._test_suites:
            # we only make it on the first use, or else we will have empty test
            # suites which may trigger failures (if fail on empty is set to
            # true
            self._test_suites[Parser.RESERVED_TEST_SUITE] = TestSuite(
                name=Parser.RESERVED_TEST_SUITE)
        self._test_suites[Parser.RESERVED_TEST_SUITE].test_cases.append(
            test_case)


class UnityParser(Parser):
    """A basic parser for the unity unit testing program."""

    REGEX_TEST = re.compile(r"^(?P<file_path>.*?):"
                            r"(?P<line_no>\d*?):"
                            r"(?P<test_name>\w*?):"
                            r"(?P<test_result>FAIL|IGNORE|PASS)"
                            r"(?::(?P<test_message>.*?))?$")
    REGEX_FINAL_LINE = re.compile(r"^(OK|FAIL)")

    class ParserState(IntEnum):
        STARTING = 0
        DONE = 1

    def __str__(self):
        return f"{self.__name__}"

    def __init__(self, name: Optional[str] = None):
        super(UnityParser, self).__init__()
        self._name = name
        self._state = UnityParser.ParserState.STARTING
        self._default_test_suite_name = name
        self._test_suites[name] = TestSuite(name=f"{name}")

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @property
    def test_suites(self) -> Optional[List[TestSuite]]:
        return list(self._test_suites.values())

    @property
    def done(self) -> bool:
        return self._state == UnityParser.ParserState.DONE

    def feed_data(self, data_chunk: bytes) -> None:
        try:
            line = data_chunk.decode('ascii')
            if UnityParser.REGEX_TEST.match(line):
                match_dict = UnityParser.REGEX_TEST.match(line).groupdict()
                test_case = TestCase(match_dict["test_name"],
                                     file=match_dict["file_path"],
                                     line=int(match_dict["line_no"]))
                test_case.stdout = line.strip().strip('\n')
                message = match_dict.get("test_message", None)
                if match_dict["test_result"] == "IGNORE":
                    test_case.add_skipped_info(message)
                elif match_dict["test_result"] == "PASS":
                    pass  # we don't modify the test case result
                else:
                    test_case.add_failure_info(message)
                self._test_suites[
                    self._default_test_suite_name].test_cases.append(test_case)

            elif UnityParser.REGEX_FINAL_LINE.match(line):
                self._transition_state(UnityParser.ParserState.DONE)
        except Exception as ec:
            self._add_parser_error(f"{ec.__name__} raised with message: {ec}.")
            self._transition_state(UnityParser.ParserState.DONE)

    def stop(self, forced: bool = False) -> None:
        if self._state != UnityParser.ParserState.DONE:
            self._transition_state(UnityParser.ParserState.DONE)
            if forced:
                self._add_parser_error(
                    "Parser stopped before unit test output stopped.")

    def _transition_state(self, new_state: ParserState) -> None:
        if new_state != self._state:
            log.debug(
                f"State transition from {self._state} -> {new_state}.")
            self._state = new_state
