from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable

ProgressCallback = Callable[[int], None]


class IDeviceLoader(ABC):

    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @abstractmethod
    def load_firmware(self, firmware_path: Path, update_progress: ProgressCallback) -> None:
        pass

    @abstractmethod
    def reset_device(self) -> None:
        pass

    @abstractmethod
    def start_program(self):
        pass

