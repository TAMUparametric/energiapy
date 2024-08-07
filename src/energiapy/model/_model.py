from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._core._aliases._is_model import IsData, IsMatrix, IsProgram, IsSystem


@dataclass
class _Model:
    """Model of the Scenario"""

    def __post_init__(self):
        self._named = False
        self._system = None
        self._data = None
        self._matrix = None
        self._program = None
        self._abstract = None
