from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .._base._simple import _Simple
from ._commodity import _Commodity


if TYPE_CHECKING:
    from ..._core._aliases._is_input import IsBoundInput


@dataclass
class Cash(_Simple, _Commodity):

    spend: IsBoundInput = field(default=None)
    earn: IsBoundInput = field(default=None)

    def __post_init__(self):
        _Simple.__post_init__(self)
        _Commodity.__post_init__(self)

    @staticmethod
    def bounds():
        """Attrs that quantify the bounds of the component"""
        return ['spend', 'earn']
