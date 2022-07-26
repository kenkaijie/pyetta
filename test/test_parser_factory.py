from typing import Optional

import pytest

from pyetta.parsers.interfaces import IParser
from pyetta.parsers.builder import ParserBuilder


def test_parser_factory_incorrect_base_class_fails():

    class FooParser:
        pass

    with pytest.raises(TypeError):
        ParserBuilder.register_parser('foo', FooParser)


def test_parser_factory_registration_works():

    class FooParser(IParser):

        def __init__(self):
            self._result = 0

        @property
        def name(self) -> str:
            return "foo"

        @classmethod
        def create_from_creation_string(cls, creation_string: str) -> 'IParser':
            return cls()

        @staticmethod
        def is_creation_string_valid(creation_string: str) -> bool:
            pass

        @property
        def result(self) -> Optional[int]:
            return self._result

        def scan_line(self, line: str) -> Optional[int]:
            self._result = 1
            return self._result

        def done(self, result: Optional[int] = 1) -> Optional[int]:
            return self._result

    ParserBuilder.register_parser('foo', FooParser)

    assert ParserBuilder.get_parser_type_by_name('foo') == FooParser
