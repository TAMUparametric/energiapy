"""Player is a class that represents a player in the Scenario
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .._base._simple import _Simple

if TYPE_CHECKING:
    from ..._core._aliases._is_input import IsBoundInput


@dataclass
class Player(_Simple):

    has: IsBoundInput = field(default=None)
    needs: IsBoundInput = field(default=None)

    def __post_init__(self):
        _Simple.__post_init__(self)

    @staticmethod
    def bounds():
        """Attrs that quantify the bounds of the component"""
        return ['has', 'needs']
