from io import IOBase
from pathlib import Path
from typing import Optional, Iterable, TextIO, BinaryIO

from pyocd.core.helpers import ConnectHelper
from pyocd.flash.file_programmer import FileProgrammer
from pyocd.flash.loader import ProgressCallback


class PyOCDLoader:
    """
    Basic built-in pyOCD loader with minimal configurations. Superclass this if you need to override
    the calls with extra functions.
    """

    def __init__(self, target: str, probe: Optional[str] = None):
        self._target = target
        self._probe = probe

    @staticmethod
    def list_targets() -> None:
        ConnectHelper.list_connected_probes()

    def load_program(self, filepath: str, progress: ProgressCallback) -> None:
        with ConnectHelper.session_with_chosen_probe(blocking=False,
                                                     return_first=True,
                                                     unique_id=self._probe) as session:
            board = session.board
            self._probe = session.probe.unique_id

            # check board matches
            if board.target_type != self._target:
                raise ValueError(f"Debugger target is not correct {board.target}.")

            programmer = FileProgrammer(session, progress=progress)
            programmer.program(file_or_path=filepath)

    def start_program(self) -> None:
        with ConnectHelper.session_with_chosen_probe(return_first=True,
                                                     unique_id=self._probe) as session:
            target = session.board.target
            target.reset_and_halt()
            target.resume()
