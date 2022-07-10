from abc import ABC, abstractmethod
from typing import Dict, Iterable

from junitparser import TestSuite
from serial import Serial

from pyetta.core.util import ICreatable, creation_string_to_dict, _T
from pyetta.parsers.interfaces import IParser


class ICapture(ABC):

    @abstractmethod
    def register_parser(self, parser: IParser):
        pass

    @abstractmethod
    def capture_and_parse_output(self) -> Iterable[TestOutcome]:
        pass


class SerialCapture(ICapture, ICreatable[ICapture]):

    def __init__(self, port: str, baud: int, *args, **kwargs):
        self._serial = Serial(port=port, baudrate=baud, timeout=30, *args, **kwargs)

    def register_parser(self, parser: IParser):
        pass

    def capture_and_parse_output(self) -> Iterable[TestSuite]:
        result = None
        while result is None:
            read_bytes = self._serial.readline()

            if read_bytes is not None and len(read_bytes) > 0:
                ascii_string = read_bytes.decode('ascii').strip('\r\n')
                click.echo(ascii_string)
                result = parser.scan_line(ascii_string)
            else:
                result = parser.done()

    @classmethod
    def from_string(cls, creation_sting, *args, **kwargs) -> _T:
        pass


class CaptureBuilder:

    _object_map: Dict[str, ICreatable[ICapture]] ={
        "serial": SerialCapture
    }

    @staticmethod
    def from_string(creation_str: str):
        creation_dict = creation_string_to_dict(creation_str)
        if 'type' not in creation_dict:
            raise KeyError("No type indicator for output type.")
        output_type = creation_dict['type']
        return CaptureBuilder._object_map[output_type].from_string(creation_dict)