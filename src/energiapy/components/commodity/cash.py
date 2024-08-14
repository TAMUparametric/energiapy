from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .._base._nature import nature
from ._commodity import _Monetary

if TYPE_CHECKING:
    from ..._core._aliases._is_input import IsBoundInput


@dataclass
class Cash(_Monetary):
    """Cash derived from:
    Resource Consume and Discharge
    Operation Capacity
    Process Produce
    Storage Store
    Transit Transport
    """

    spend: IsBoundInput = field(default=None)
    earn: IsBoundInput = field(default=None)

    def __post_init__(self):
        _Monetary.__post_init__(self)

    @staticmethod
    def collection():
        """The collection in scenario"""
        return 'cash'

    @staticmethod
    def bounds():
        """Attrs that quantify the bounds of the component"""
        return nature['cash']['bounds']

    @classmethod
    def inputs(cls):
        """Attrs"""
        return cls.bounds()
