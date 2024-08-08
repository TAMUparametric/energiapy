from __future__ import annotations

from typing import TYPE_CHECKING

from dataclasses import dataclass, field

from .._component import _Asset

if TYPE_CHECKING:
    from ..._core._aliases._is_input import IsBoundInput, IsExactInput


@dataclass
class Land(_Asset):
    """Land derived from Operation Capacity"""

    use: IsBoundInput = field(default=None)
    cost: IsExactInput = field(default=None)

    def __post_init__(self):
        _Asset.__post_init__(self)

    @staticmethod
    def collection():
        """The collection in scenario"""
        return 'assets'
