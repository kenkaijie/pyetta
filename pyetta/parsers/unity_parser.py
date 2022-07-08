import re
from enum import IntEnum
from typing import Optional, Dict, Match, Any, Iterable, Tuple

import logging

from pyetta.parsers.interfaces import IParser

log = logging.getLogger(__name__)


class UnityParser(IParser):
    """
    A basic parser for the unity unit testing program.

        usage: type=unity

        This parser does not have any additional arguments.
    """
    PARSER_NAME = 'unity'
    REGEX_CREATION_STRING = re.compile(r"^type=unity$")
    REGEX_FINAL_LINE_PASS = re.compile(r"^OK$")
    REGEX_FINAL_LINE_FAIL = re.compile(r"^FAIL$")

    @property
    def name(self) -> str:
        return UnityParser.PARSER_NAME

    @classmethod
    def create_from_creation_string(cls, creation_string: str) -> 'UnityParser':
        return cls()

    @staticmethod
    def is_creation_string_valid(creation_string: str) -> bool:
        return UnityParser.REGEX_CREATION_STRING.match(creation_string) is not None

    class ParserState(IntEnum):
        STARTING = 0
        DONE = 1

    def __init__(self):
        self._state = UnityParser.ParserState.STARTING
        self._result = None

    def _transition_state(self, new_state: ParserState) -> None:
        if new_state != self._state:
            log.debug(f"Transitioning parser from {self._state} -> {new_state}")
            self._state = new_state

    @property
    def result(self) -> Optional[int]:
        return self._result

    @result.setter
    def result(self, value: Optional[int]) -> None:
        self._result = value

    def scan_line(self, line: str) -> Optional[int]:
        if UnityParser.REGEX_FINAL_LINE_PASS.match(line):
            self.result = 0
            self._transition_state(UnityParser.ParserState.DONE)
        elif UnityParser.REGEX_FINAL_LINE_PASS.match(line):
            self.result = 1
            self._transition_state(UnityParser.ParserState.DONE)

        return self.result

    def done(self, result: Optional[int] = 1) -> Optional[int]:
        if self._state != UnityParser.ParserState.DONE:
            self.result = result
            self._transition_state(UnityParser.ParserState.DONE)
        return self.result
