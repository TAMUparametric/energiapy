"""Attr Block 
Handles the attributes of components
Defines strict behaviour
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ..core.aliases.is_input import IsBoundInput


@dataclass
class Bounds:
    # Player
    has: IsBoundInput = field(default=None)
    needs: IsBoundInput = field(default=None)
    # Cash
    spend: IsBoundInput = field(default=None)
    earn: IsBoundInput = field(default=None)
    # Emission
    emit: IsBoundInput = field(default=None)
    # Land and Material (Used)
    use: IsBoundInput = field(default=None)
    # Resource
    buy: IsBoundInput = field(default=None)
    sell: IsBoundInput = field(default=None)
    ship: IsBoundInput = field(default=None)
    # Operational
    capacity: IsBoundInput = field(default=True)
    # Process
    produce: IsBoundInput = field(default=None)
    # Storage
    capacity_c: IsBoundInput = field(default=None)
    capacity_d: IsBoundInput = field(default=None)
    store: IsBoundInput = field(default=None)
    # Transit
    transport: IsBoundInput = field(default=None)


@dataclass
class Collects:
    expense = []
    emission = []
    land = []


@dataclass
class Exacts:
    # Land and Material (Used)
    cost: IsExactInput = field(default=None)
    emission: IsExactInput = field(default=None)
    # Resource
    buy_price: IsExactInput = field(default=None)
    sell_price: IsExactInput = field(default=None)
    credit: IsExactInput = field(default=None)
    penalty: IsExactInput = field(default=None)
    buy_emission: IsExactInput = field(default=None)
    sell_emission: IsExactInput = field(default=None)
    loss_emission: IsExactInput = field(default=None)
    # Operational
    land: IsExactInput = field(default=None)
    material: IsExactInput = field(default=None)
    capex: IsExactInput = field(default=None)
    opex: IsExactInput = field(default=None)
    emission: IsExactInput = field(default=None)


@dataclass
class BoundsRes:
    # Process
    buy: IsBoundInput = field(default=None)
    sell: IsBoundInput = field(default=None)
    # Transit
    ship: IsBoundInput = field(default=None)


@dataclass
class ExactRes:
    # Process
    buy_price: IsExactInput = field(default=None)
    sell_price: IsExactInput = field(default=None)
    credit: IsExactInput = field(default=None)
    penalty: IsExactInput = field(default=None)


@dataclass
class Balances:
    # Process
    conversion: IsConvInput = field(default=None)
    # Transit
    freight: IsResource = field(default=None)


@dataclass
class Attr:
    name: str

    def __post_init__(self):
        self.name = str(self.name)

    # Player

    # Cash
    # Emission
    # Land and Material (Used)
    # Resource
    # Operational
    # Process
    locations: List[IsLocation] = field(default=None)
    # Storage
    loss: IsExactInput = field(default=None)
    inventory: IsInvInput = field(default=None)
    locations: List[IsLocation] = field(default=None)
    # Transit
    loss: IsExactInput = field(default=None)
    linkages: List[IsLinkage] = field(default=None)
    # deliver: IsBoundInput = field(default=None)
