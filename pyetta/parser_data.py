"""pyetta defined test data format."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class TestResult(Enum):
    Pass = "Pass"
    Fail = "Fail"
    Skip = "Skip"


@dataclass()
class TestCase:
    name: str
    result: TestResult
    group: Optional[str] = None
    filepath: Optional[str] = None
    extra: Dict[Any, Any] = field(default_factory=dict)
    line_num: int = 0
    runtime_s: float = 0.0
    timestamp_s: float = 0.0
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    result_message: Optional[str] = None
