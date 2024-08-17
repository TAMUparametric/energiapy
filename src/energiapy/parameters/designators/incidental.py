"""If a parameter is incidental
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..._core._handy._dunders import _Dunders

if TYPE_CHECKING:
    from ..._core._aliases._is_input import IsIncidental


@dataclass
class I(_Dunders):
    """Incidental parameter"""

    value: IsIncidental = field(default=None)

    def __post_init__(self):
        self.name = 'i'
