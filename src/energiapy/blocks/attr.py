""" This has three objects
AttrBlock: 
    individual attributes of Components
AttrCollections:
    collections of Component attributes 
    this is helpful when component attributes are declared at other Components
Attr:
    All AttrBlocks, there is only one instance of this in the Scenario
    Handles the attributes of components
    Defines strict behaviour
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import List, TYPE_CHECKING

from ..core._handy._dunders import _Dunders
from ..components.analytical.player import Player
from ..components.commodity.cash import Cash
from ..components.commodity.emission import Emission
from ..components.commodity.land import Land
from ..components.commodity.material import Material
from ..components.commodity.resource import Resource
from ..components.operational.process import Process
from ..components.operational.storage import Storage
from ..components.operational.transit import Transit

if TYPE_CHECKING:
    from ..core.aliases.is_component import IsComponent
    from ..core.aliases.is_input import (
        IsBoundInput,
        IsExactInput,
        IsBalInput,
        IsConvInput,
    )


@dataclass
class AttrBlock(_Dunders):
    """Attr Block
    Handles the attributes of components
    Defines strict behaviour

    Attributes:
        name (str): The name of the attribute block
    """

    name: str = field(default=None)
    cmp: List[IsComponent] = field(default_factory=list)

    def __post_init__(self):
        self.name = f'Attr|{self.name}|'
        # Collections associated with the attribute
        self.values = []
        self.parameters = []
        self.constraints = []
        self.variables = []
        self.dispositions = []


@dataclass
class AttrCollection(_Dunders):
    """Attr is a collection of AttrBlocks

    Attributes:
        name (str): The name of the attribute collection

    """

    name: str = field(default=None)
    attrblocks: List[AttrBlock] = field(default_factory=list)

    def __post_init__(self):
        self.name = f'Attr|{self.name}|'
        # Collections associated with the attribute
        self.values = sum([attr.values for attr in self.attrblocks], [])
        self.parameters = sum([attr.parameters for attr in self.attrblocks], [])
        self.dispositions = sum([attr.dispositions for attr in self.attrblocks], [])
        self.constraints = sum([attr.constraints for attr in self.attrblocks], [])
        self.variables = sum([attr.variables for attr in self.attrblocks], [])


@dataclass
class PlyBounds:
    """Bounds for Players"""

    has: IsBoundInput = field(default=None)
    needs: IsBoundInput = field(default=None)


@dataclass
class CshBounds:
    """Bounds for Cash"""

    spend: IsBoundInput = field(default=None)
    earn: IsBoundInput = field(default=None)


@dataclass
class UsedBounds:
    """Bounds for Land and Material (Used)"""

    use: IsBoundInput = field(default=None)


@dataclass
class ResBounds:
    """Bounds for Resources"""

    buy: IsBoundInput = field(default=None)
    sell: IsBoundInput = field(default=None)
    ship: IsBoundInput = field(default=None)


@dataclass
class OpnBounds:
    """Bounds for Operational Components"""

    capacity: IsBoundInput = field(default=None)
    operate: IsBoundInput = field(default=None)


@dataclass
class Bounds(PlyBounds, CshBounds, UsedBounds, ResBounds, OpnBounds):
    """These are Bounds for the Components

    Bounds can be different for Network and individual Spatial Components
    """

    def __post_init__(self):
        # Player
        self.has = AttrBlock(name='has', cmp=[Player])
        self.needs = AttrBlock(name='needs', cmp=[Player])
        # Cash
        self.spend = AttrBlock(name='spend', cmp=[Cash])
        self.earn = AttrBlock(name='earn', cmp=[Cash])
        # Emission
        self.emit = AttrBlock(name='emit', cmp=[Emission])
        # Land and Material (Used)
        self.use = AttrBlock(name='use', cmp=[Land, Material])
        # Resource
        self.buy = AttrBlock(name='buy', cmp=[Resource])
        self.sell = AttrBlock(name='sell', cmp=[Resource])
        self.ship = AttrBlock(name='ship', cmp=[Resource])
        # Operational
        self.capacity = AttrBlock(name='capacity', cmp=[Process, Storage, Transit])
        self.operate = AttrBlock(name='operate', cmp=[Process, Storage, Transit])


@dataclass
class ResExacts:
    """Exact Inputs for Resources"""

    buy_price: IsExactInput = field(default=None)
    sell_price: IsExactInput = field(default=None)
    credit: IsExactInput = field(default=None)
    penalty: IsExactInput = field(default=None)
    buy_emission: IsExactInput = field(default=None)
    sell_emission: IsExactInput = field(default=None)
    loss_emission: IsExactInput = field(default=None)


@dataclass
class UsedExacts:
    """Exact Inputs for Land and Material (Used)"""

    cost: IsExactInput = field(default=None)


@dataclass
class OpnExacts:
    """Exact Inputs for Operational Components"""

    land: IsExactInput = field(default=None)
    material: IsExactInput = field(default=None)
    capex: IsExactInput = field(default=None)
    opex: IsExactInput = field(default=None)
    emission: IsExactInput = field(default=None)


@dataclass
class Exacts(ResExacts, UsedExacts, OpnExacts):
    """These are Exact Component Inputs

    These are inherited across all Spatial Components
    if defined at Network

    There is no Network value for these

    """

    def __post_init__(self):
        # Land and Material (Used)
        self.cost = AttrBlock(name='cost', cmp=[Land, Material])
        # Resource
        self.buy_price = AttrBlock(name='buy_price', cmp=[Resource])
        self.sell_price = AttrBlock(name='sell_price', cmp=[Resource])
        self.credit = AttrBlock(name='credit', cmp=[Resource])
        self.penalty = AttrBlock(name='penalty', cmp=[Resource])
        self.buy_emission = AttrBlock(name='buy_emission', cmp=[Resource])
        self.sell_emission = AttrBlock(name='sell_emission', cmp=[Resource])
        self.loss_emission = AttrBlock(name='loss_emission', cmp=[Resource])
        # Operational
        self.land = AttrBlock(name='land', cmp=[Process, Storage, Transit])
        self.material = AttrBlock(name='material', cmp=[Process, Storage, Transit])
        self.capex = AttrBlock(name='capex', cmp=[Process, Storage, Transit])
        self.opex = AttrBlock(name='opex', cmp=[Process, Storage, Transit])
        self.emission = AttrBlock(
            name='emission', cmp=[Process, Storage, Transit, Land, Material]
        )


@dataclass
class ProBalances:
    """Balances for Players"""

    conversion: IsConvInput = field(default=None)


@dataclass
class StgBalances:
    """Balances for Storage"""

    inventory: IsBalInput = field(default=None)


@dataclass
class TrnBalances:
    """Balances for Transit"""

    freight: IsBalInput = field(default=None)


@dataclass
class Balances(ProBalances, StgBalances, TrnBalances):
    """These are Balances for Resources
    defined at Operational Components
    """

    def __post_init__(self):
        # Process
        self.conversion = AttrBlock(name='conversion', cmp=[Process])
        # Storage
        self.inventory = AttrBlock(name='inventory', cmp=[Storage])
        # Transit
        self.freight = AttrBlock(name='freight', cmp=[Transit])


@dataclass
class Attr(Bounds, Exacts, Balances, _Dunders):
    """This object collects all the attributes defined
    and makes a list of Dispositions they are defined at

    """

    name: str = field(default=None)

    def __post_init__(self):
        self.name = f'Attr|{self.name}|'
        Bounds.__post_init__(self)
        Exacts.__post_init__(self)
        Balances.__post_init__(self)

    @staticmethod
    def bounds():
        """Returns all Bounds"""
        return fields(Bounds)

    @staticmethod
    def exacts():
        """Returns all Exacts"""
        return fields(Exacts)

    @staticmethod
    def balances():
        """Returns all Balances"""
        return fields(Balances)

    @property
    def expenses(self):
        """Expenses"""
        return AttrCollection(
            name='expenses',
            attrblocks=[
                self.capex,
                self.opex,
                self.buy_price,
                self.sell_price,
                self.credit,
                self.penalty,
                self.cost,
            ],
        )

    @property
    def emissions(self):
        """Emissions"""
        return AttrCollection(
            name='emissions',
            attrblocks=[
                self.buy_emission,
                self.sell_emission,
                self.loss_emission,
                self.emission,
            ],
        )

    @property
    def lnduses(self):
        """Land Uses"""
        return AttrCollection(name='lnduses', attrblocks=[self.land])

    @property
    def matuses(self):
        """Material Uses"""
        return AttrCollection(name='matuses', attrblocks=[self.material])
