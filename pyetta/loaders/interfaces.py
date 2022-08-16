from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable

ProgressCallback = Callable[[int], None]


class Loader(ABC):

    @property
    @abstractmethod
    def target(self):
        pass

    @property
    @abstractmethod
    def firmware_path(self):
        pass

    @abstractmethod
    def __enter__(self):
        """Starts the loader.
        """
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @abstractmethod
    def load_firmware(self, update_progress: ProgressCallback) -> None:
        pass

    @abstractmethod
    def reset_device(self) -> None:
        pass

    @abstractmethod
    def start_program(self):
        pass

