from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..._base._defined import _Trade

if TYPE_CHECKING:
    from ...._core._aliases._is_input import IsBoundInput, IsExactInput


@dataclass
class Material(_Trade):

    use: IsBoundInput = field(default=None)
    price: IsExactInput = field(default=None)

    def __post_init__(self):
        _Trade.__post_init__(self)

    @staticmethod
    def collection():
        """The collection in scenario"""
        return 'materials'
