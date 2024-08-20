"""Emission component, measured on the basis of impact potential 
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .._base._simple import _Simple
from ._commodity import _Commodity

if TYPE_CHECKING:
    from ..._core._aliases._is_input import IsBoundInput


@dataclass
class Emission(_Simple, _Commodity):
    """Emission are generated by Commodity use, buy, sell
    and setting up and running Operation

    Attributes:
        emit (IsBoundInput): bound on amount emitted at some spatiotemporal disposition
        basis (str): basis of the component
        citation (dict): citation of the component
        block (str): block of the component
        introduce (str): index in scale when the component is introduced
        retire (str): index in scale when the component is retired
        label (str): label of the component
    """

    emit: IsBoundInput = field(default=None)

    def __post_init__(self):
        _Simple.__post_init__(self)
        _Commodity.__post_init__(self)

    @staticmethod
    def bounds():
        """Attrs that quantify the bounds of the component"""
        return ['emit']
