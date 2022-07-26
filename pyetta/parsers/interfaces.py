from abc import ABC, abstractmethod
from typing import List

from junit_xml import TestSuite


class IParser(ABC):

    @abstractmethod
    def scan_line(self, line: str) -> None:
        pass

    @abstractmethod
    def abort(self) -> None:
        pass

    @property
    @abstractmethod
    def done(self) -> bool:
        pass

    @property
    @abstractmethod
    def test_suites(self) -> List[TestSuite]:
        pass
