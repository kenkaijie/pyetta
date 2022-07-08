from typing import AnyStr, Dict, Type, Iterable, Tuple

from pyetta.parsers.interfaces import IParser
from pyetta.parsers.unity_parser import UnityParser

# Built-in supported parsers
_supported_parsers: Dict[AnyStr, Type[IParser]] = {
        'unity': UnityParser
}


class ParserFactory:

    @staticmethod
    def supported_parsers() -> Iterable[Tuple[str, Type[IParser]]]:
        return _supported_parsers.items()

    @staticmethod
    def register_parser(parser_name: str, parser_type: Type[IParser]):
        if not issubclass(parser_type, IParser):
            raise TypeError("Needs to be a subclass of IParser.")
        _supported_parsers.update({parser_name: parser_type})

    @staticmethod
    def get_parser_type_by_name(parser_name: str) -> Type[IParser]:
        return _supported_parsers[parser_name]

    @staticmethod
    def create_by_name(parser_name: str, *args, **kwargs) -> IParser:
        return _supported_parsers[parser_name](*args, **kwargs)

    @staticmethod
    def create_by_creation_string(creation_string: str) -> IParser:
        for parser in _supported_parsers.values():
            if parser.is_creation_string_valid(creation_string):
                return parser.create_from_creation_string(creation_string)

        raise KeyError("No parsers support this creation string.")
