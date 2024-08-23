"""Poishe, Money 
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .._base._simple import _Simple
from ._commodity import _Commodity

if TYPE_CHECKING:
    from ..._core._aliases._is_input import IsBoundInput


@dataclass
class Cash(_Simple, _Commodity):
    """Cash is an Asset
    The amount spent or earned at some spatiotemporal dispoqition can be bound

    Attributes:
        spend (IsBoundInput): bound on amount spent
        earn (IsBoundInput): bound on amount earned
        basis (str): basis of the component
        citation (dict): citation of the component
        block (str): block of the component
        introduce (str): index in scale when the component is introduced
        retire (str): index in scale when the component is retired
        label (str): label of the component
    """

    spend: IsBoundInput = field(default=None)
    earn: IsBoundInput = field(default=None)

    def __post_init__(self):
        _Simple.__post_init__(self)
        _Commodity.__post_init__(self)
        self.expense = []

    @staticmethod
    def bounds():
        """Attrs that quantify the bounds of the component"""
        return ['spend', 'earn']
