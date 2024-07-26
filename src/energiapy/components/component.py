"""These are methods that are common to all Component dataclasses
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..core.general import ClassName, Dunders, Magics
from ..core.handle import HandleAspects
from ..core.onset import CompInits, ElementCols

if TYPE_CHECKING:
    from ..type.alias import IsComponent, IsValue
    from .horizon import Horizon


@dataclass
class Component(CompInits, ElementCols, Magics, Dunders, ClassName, HandleAspects):
    """Most energiapy components are inherited from this.
    Some like Horizon, TemporalScale, Scenario only take a subset of the methods 
    """

    def __post_init__(self):
        CompInits.__post_init__(self)
        ElementCols.__post_init__(self)

