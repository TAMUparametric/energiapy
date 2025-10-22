"""Interact"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .player import Player


class Interact:
    """Interaction between Players
    
    :param player1: First player
    :type player1: Player
    :param player2: Second player
    :type player2: Player
    """

    player1: Player = None
    player2: Player = None
