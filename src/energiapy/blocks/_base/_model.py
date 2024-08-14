from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..._core._aliases._is_block import (IsData, IsMatrix, IsProgram,
                                             IsSystem)


@dataclass
class _Model:
    """Model of the Scenario"""

    def __post_init__(self):
        self.named = False
        self._system = None
        self._data = None
        self._matrix = None
        self._program = None
        self._abstract = None

