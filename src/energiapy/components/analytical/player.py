"""Player is a class that represents a player in the Scenario
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .._initialize._component import _Component

if TYPE_CHECKING:
    from ..type.alias import IsCan, IsOwns


@dataclass
class Player(_Component):
    """Player in the Scenario
    has control over some Operations 
    can give or take commodities from other Players 
    """
    owns: IsOwns = field(default=None)
    has: IsCan = field(default=None)
    needs: IsCan = field(default=None)

    def __post_init__(self):
        _Component.__post_init__(self)

    @property
    def collection(self):
        """The collection in scenario
        """
        return 'players'
