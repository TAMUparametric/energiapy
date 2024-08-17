"""Player is a class that represents a player in the Scenario
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .._base._nature import nature
from ._analytical import _Analytical

if TYPE_CHECKING:
    from ..._core._aliases._is_input import IsBoundInput


@dataclass
class Player(_Analytical):
    """Player in the Scenario
    has control over some Operations
    can give or take commodities from other Players
    """

    has: IsBoundInput = field(default=None)
    needs: IsBoundInput = field(default=None)

    def __post_init__(self):
        _Analytical.__post_init__(self)


    @staticmethod
    def bounds():
        """Attrs that quantify the bounds of the component"""
        return nature['player']['bounds']

    @classmethod
    def inputs(cls):
        """Attrs"""
        return cls.bounds()


