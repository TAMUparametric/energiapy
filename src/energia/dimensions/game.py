"""System"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .._core._dimension import _Dimension

if TYPE_CHECKING:
    from ..components.game.couple import Interact
    from ..components.game.player import Player

@dataclass
class Game(_Dimension):
    """
    System representation as a Resource Task Network (RTN)
    All resources and tasks are attached to this object

    :param model: Model to which the representation belongs.
    :type model: Model

    :ivar name: Name of the dimension, generated based on the class and model name.
    :vartype name: str
    :ivar players: List of players. Defaults to [].
    :vartype players: list[Player]
    :ivar couples: List of couples. Defaults to [].
    :vartype couples: list[Couple]
    """

    def __post_init__(self):
        # ------------Decision-Makers----------------------
        self.players: list[Player] = []
        self.interacts: list[Interact] = []

        _Dimension.__post_init__(self)
