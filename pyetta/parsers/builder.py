from typing import AnyStr, Dict, Type, Iterable, Tuple

from pyetta.parsers.interfaces import IParser
from pyetta.parsers.unity_parser import UnityParser


class ParserBuilder:

    _supported_parsers: Dict[AnyStr, Type[IParser]] = {
        'unity': UnityParser
    }

    @staticmethod
    def supported_parsers() -> Iterable[Tuple[str, Type[IParser]]]:
        return ParserBuilder._supported_parsers.items()

    @staticmethod
    def register_parser(parser_name: str, parser_type: Type[IParser]):
        if not issubclass(parser_type, IParser):
            raise TypeError("Needs to be a subclass of IParser.")
        ParserBuilder._supported_parsers.update({parser_name: parser_type})

    @staticmethod
    def get_parser_type_by_name(parser_name: str) -> Type[IParser]:
        return ParserBuilder._supported_parsers[parser_name]

    @staticmethod
    def from_name(parser_name: str) -> IParser:
        if parser_name not in ParserBuilder._supported_parsers:
            raise KeyError(f"No supported parsers by name {parser_name}.")
        return ParserBuilder._supported_parsers[parser_name]()
