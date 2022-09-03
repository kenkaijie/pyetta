import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable
from typing import Optional

from pyocd.core.helpers import ConnectHelper
from pyocd.core.session import Session
from pyocd.flash.file_programmer import FileProgrammer

log = logging.getLogger("pyetta.loaders")


class Loader(ABC):

    @abstractmethod
    def load_to_device(self,
                       progress: Optional[Callable[[int], None]] = None) -> None:
        """Loads the target data into the device. Optionally can report progress to a callback if
        one is given.

        :param progress: Callback to allow progress to be reported. Callback
                         should take in a single int representing the
                         percentage completion [0-100].
        """

    @abstractmethod
    def reset_device(self) -> None:
        """Resets the device. This can be either a software or hardware reset depending on the
        implementation. The expected result of this reset is that all internal states of the device
        are reset into their default values on startup."""

    @abstractmethod
    def start_program(self) -> None:
        """Starts the loaded program from the beginning. Each subsequent run of the program should
        have its state unaffected by previous run."""


class PyOCDDeviceLoader(Loader):
    """
    Basic built-in pyOCD loader with minimal configurations. Superclass this if
    you need to override the calls with extra functions.
    """

    def __init__(self, firmware_path: Path, target: Optional[str] = None,
                 probe: Optional[str] = None):
        self._target = target
        self._firmware_path = firmware_path
        self._probe = probe
        self._session: Optional[Session] = None

    def __str__(self):
        return f"PyOCD Loader, file='{self._firmware_path}', target='{self._target or 'auto'}'"

    def __enter__(self):
        self._session = ConnectHelper.session_with_chosen_probe(blocking=False,
                                                                return_first=True,
                                                                unique_id=self._probe,
                                                                auto_open=True)
        if self._session is not None:
            self._session.__enter__()
            self._board = self._session.board
            if self._target is not None and self._board.target_type != self._target:
                raise ValueError(
                    f"Debugger target is not correct {self._board.target_type}.")
            return self
        else:
            raise RuntimeError("Unable to open connection for loader.")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._board = None
        if self._session is not None:
            return self._session.__exit__(exc_type, exc_val, exc_tb)

    def load_to_device(self,
                       progress: Optional[Callable[[int], None]] = None) -> None:
        programmer = FileProgrammer(self._session, progress=progress)
        programmer.program(file_or_path=str(self._firmware_path.resolve()))

    def reset_device(self) -> None:
        self._board.target.reset()

    def start_program(self):
        self._board.target.reset_and_halt()
        self._board.target.resume()
