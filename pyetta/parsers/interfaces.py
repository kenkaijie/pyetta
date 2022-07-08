from abc import ABC, abstractmethod
from typing import Optional, Iterable, Tuple


class IParser(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @classmethod
    @abstractmethod
    def create_from_creation_string(cls, creation_string: str) -> 'IParser':
        pass

    @staticmethod
    @abstractmethod
    def is_creation_string_valid(creation_string: str) -> bool:
        pass

    @property
    @abstractmethod
    def result(self) -> Optional[int]:
        pass

    @abstractmethod
    def scan_line(self, line: str) -> Optional[int]:
        pass

    @abstractmethod
    def done(self, result: Optional[int] = 1) -> Optional[int]:
        pass
