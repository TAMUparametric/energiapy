"""Player is a class that represents a player in the Scenario
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..type.alias import IsCan, IsOwns


@dataclass
class Player:
    """Player in the Scenario
    has control over some Operations 
    can give or take commodities from other Players 
    """
    name: str = field(default=None)
    owns: IsOwns = field(default_factory=None)
    can_give: IsCan = field(default_factory=None)
    can_take: IsCan = field(default_factory=None)
    label: str = field(default=None)
