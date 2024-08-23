"""Player is a class that represents a player in the Scenario
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .._base._simple import _Simple

if TYPE_CHECKING:
    from ...core.aliases.is_input import IsBoundInput


@dataclass
class Player(_Simple):
    """A Player in the Scenario

    Attributes:
        has (IsBoundInput): how much of particular commodity the player has
        needs (IsBoundInput): how much of particular commodity the player needs
        basis (str): basis of the component
        citation (dict): citation of the component
        block (str): block of the component
        introduce (str): index in scale when the component is introduced
        retire (str): index in scale when the component is retired
        label (str): label of the component

    """

    has: IsBoundInput = field(default=None)
    needs: IsBoundInput = field(default=None)

    def __post_init__(self):
        _Simple.__post_init__(self)

    @staticmethod
    def bounds():
        """Attrs that quantify the bounds of the component"""
        return ['has', 'needs']
