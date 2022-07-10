from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Iterable, Union

from junitparser import TestSuite

from pyetta.core.util import creation_string_to_dict, ICreatable, _T


class IOutputter(ABC):

    @abstractmethod
    def generate_output(self, test_outcomes: Union[TestSuite, Iterable[TestSuite]]) -> None:
        pass


class StdOutOutputter(IOutputter, ICreatable[IOutputter]):
    def generate_output(self, test_outcomes: Union[TestSuite, Iterable[TestSuite]]) -> None:
        if not isinstance(test_outcomes, Iterable):
            test_outcomes = [test_outcomes]

        for test_outcome in test_outcomes:
            print(f"{test_outcome}")

    @classmethod
    def from_string(cls, creation_sting, *args, **kwargs) -> 'StdOutOutputter':
        return cls()


class OutputBuilder:

    _object_map: Dict[str, ICreatable[IOutputter]] = {
        "stdout": StdOutOutputter
    }

    @staticmethod
    def from_string(creation_str: str) -> IOutputter:
        creation_dict = creation_string_to_dict(creation_str)
        if 'type' not in creation_dict:
            raise KeyError("No type indicator for output type.")
        output_type = creation_dict['type']
        return OutputBuilder._object_map[output_type].from_string(creation_dict)