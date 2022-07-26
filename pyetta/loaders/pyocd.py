from pathlib import Path
from typing import Optional

from pyocd.core.helpers import ConnectHelper
from pyocd.flash.file_programmer import FileProgrammer

from pyetta.loaders.interfaces import IDeviceLoader, ProgressCallback


class PyOCDDeviceLoader(IDeviceLoader):
    """
    Basic built-in pyOCD loader with minimal configurations. Superclass this if you need to override
    the calls with extra functions.
    """

    def __init__(self, target: str, probe: Optional[str] = None):
        self._target = target
        self._probe = probe
        self._session = ConnectHelper.session_with_chosen_probe(blocking=False,
                                                                return_first=True,
                                                                unique_id=self._probe,
                                                                auto_open=True)

    def __enter__(self):
        self._session.__enter__()
        self._board = self._session.board
        if self._board.target_type != self._target:
            raise ValueError(f"Debugger target is not correct {self._board.target_type}.")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._board = None
        return self._session.__exit__(exc_type, exc_val, exc_tb)

    def load_firmware(self, firmware_path: Path, progress: ProgressCallback) -> None:
        programmer = FileProgrammer(self._session, progress=progress)
        programmer.program(file_or_path=str(firmware_path))

    def reset_device(self) -> None:
        self._board.target.reset()

    def start_program(self):
        self._board.target.reset_and_halt()
        self._board.target.resume()
