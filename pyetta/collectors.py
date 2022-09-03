from abc import ABC, abstractmethod
from typing import IO


class Collector(ABC):
    """Pyetta collector class, provides a small abstraction to allow for the collection of data.

    .. note::
        Timeouts if relevant should be handled by the constructor,
    """

    @abstractmethod
    def read_chunk(self) -> bytes:
        """Reads a chunk of data.

        A chunk is defined as a single continuous piece that a parser can use to extract one of
        more tests from. Each chunk should have a whole piece of data."""


class IOBaseCollector(Collector):
    """Base helper wrapping class that covers all base IO collectors."""

    def __init__(self, io_base: IO):
        super().__init__()
        self._io = io_base

    def __enter__(self):
        return self._io.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._io.__exit__(exc_type, exc_val, exc_tb)

    def read_chunk(self) -> bytes:
        return self._io.readline()
