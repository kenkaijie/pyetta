import re
from enum import IntEnum
from typing import Dict, Any, List

import logging

from junit_xml import TestSuite, TestCase

from pyetta.parsers.interfaces import IParser

log = logging.getLogger(__name__)


class UnityParser(IParser):
    """A basic parser for the unity unit testing program."""

    REGEX_TEST = re.compile(r"(?P<file_path>.*?):(?P<line_no>\d*?):(?P<test_name>\w*?):(?P<test_result>FAIL|IGNORE|PASS)(?::(?P<test_message>.*?))?")
    REGEX_FINAL_LINE = re.compile(r"^(OK|FAIL)")

    class ParserState(IntEnum):
        STARTING = 0
        DONE = 1

    def __init__(self):
        self._state = UnityParser.ParserState.STARTING
        self._test_suites: Dict[Any, TestSuite] = {None: TestSuite(name="none")}

    @property
    def test_suites(self) -> List[TestSuite]:
        return list(self._test_suites.values())

    @property
    def done(self) -> bool:
        return self._state == UnityParser.ParserState.DONE

    def scan_line(self, line: str) -> None:
        if UnityParser.REGEX_TEST.match(line):
            match_dict = UnityParser.REGEX_TEST.match(line).groupdict()
            test_case = TestCase(match_dict["test_name"], file=match_dict["file_path"],
                                 line=int(match_dict["line_no"]))
            test_case.stdout = line
            message = match_dict.get("test_message", "")
            if match_dict["test_result"] == "IGNORE":
                test_case.add_skipped_info(message)
            elif match_dict["test_result"] == "PASS":
                pass  # we don't modify the test case result
            else:
                test_case.add_failure_info(message)
            self._test_suites[None].test_cases.append(test_case)

        elif UnityParser.REGEX_FINAL_LINE.match(line):
            self._transition_state(UnityParser.ParserState.DONE)

    def abort(self) -> None:
        if self._state != UnityParser.ParserState.DONE:
            self._transition_state(UnityParser.ParserState.DONE)

    def _transition_state(self, new_state: ParserState) -> None:
        if new_state != self._state:
            log.debug(f"Transitioning parser from {self._state} -> {new_state}")
            self._state = new_state
