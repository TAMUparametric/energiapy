from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .._base._defined import _Commodity

if TYPE_CHECKING:
    from ..._core._aliases._is_input import IsBoundInput, IsExactInput


@dataclass
class Material(_Commodity):

    use: IsBoundInput = field(default=None)
    use_price: IsExactInput = field(default=None)

    def __post_init__(self):
        _Commodity.__post_init__(self)

    @staticmethod
    def quantify():
        """The quantified data inputs to the component"""
        return ['use']

    @staticmethod
    def expenses():
        """The expense data inputs to the component"""
        return ['use_price']

    @staticmethod
    def collection():
        """The collection in scenario"""
        return 'materials'
