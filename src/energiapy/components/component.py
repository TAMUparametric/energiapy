"""These are methods that are common to all Component dataclasses
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..core.general import ClassName, Dunders, Magics
from ..core.handle import HandleAspects
from ..core.onset import CompInits, ElementCols
from ..core.impact import Impact, ImpactCap
from ..core.bookkeeping import BookKeeping
from ..core.existence import Existence
from ..core.expense import SpcExpense, OpnExpense
from ..core.land import OpnLand, SpcLand

if TYPE_CHECKING:
    from ..type.alias import IsComponent, IsValue
    from .horizon import Horizon


@dataclass
class Component(CompInits, ElementCols, Magics, Dunders, ClassName, HandleAspects):
    """Most energiapy components are inherited from this.
    Some like Horizon, Scale, Scenario only take a subset of the methods 
    """

    def __post_init__(self):
        CompInits.__post_init__(self)
        ElementCols.__post_init__(self)


@dataclass
class Commodity(Component, Impact, BookKeeping):
    """A Commodity is a good or service that is produced, consumed, or traded in the model.
    Resource and Material are special cases of Commodity.
    """

    def __post_init__(self):
        Commodity.__post_init__(self)


@dataclass
class Operation(Component, OpnExpense, Impact, OpnLand, Existence, BookKeeping):
    """An Operation is a process that transforms commodities.
    Process, Storage, and Transport are special cases of Operation. 
    """

    def __post_init__(self):
        Component.__post_init__(self)


@dataclass
class Space(Component, SpcExpense, SpcLand, ImpactCap, BookKeeping):
    """Space is a location where operations are performed.
    Location, Linkage, Network are special cases of Space.
    """

    def __post_init__(self):
        Component.__post_init__(self)
