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
class Bounds:
    """These are Bounds for the Components

    Bounds can be different for Network and individual Spatial Components

    """

    has: AttrBlock = field(default=None)
    needs: AttrBlock = field(default=None)
    spend: AttrBlock = field(default=None)
    earn: AttrBlock = field(default=None)
    emit: AttrBlock = field(default=None)
    use: AttrBlock = field(default=None)
    buy: AttrBlock = field(default=None)
    sell: AttrBlock = field(default=None)
    ship: AttrBlock = field(default=None)
    capacity: AttrBlock = field(default=None)
    operate: AttrBlock = field(default=None)

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
class Exacts:
    """These are Exact Component Inputs

    These are inherited across all Spatial Components
    if defined at Network

    There is no Network value for these

    """

    cost: AttrBlock = field(default=None)
    buy_price: AttrBlock = field(default=None)
    sell_price: AttrBlock = field(default=None)
    credit: AttrBlock = field(default=None)
    penalty: AttrBlock = field(default=None)
    buy_emission: AttrBlock = field(default=None)
    sell_emission: AttrBlock = field(default=None)
    loss_emission: AttrBlock = field(default=None)
    land: AttrBlock = field(default=None)
    material: AttrBlock = field(default=None)
    capex: AttrBlock = field(default=None)
    opex: AttrBlock = field(default=None)
    emission: AttrBlock = field(default=None)

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
class Balances:
    """These are Balances for Resources
    defined at Operational Components
    """

    conversion: AttrBlock = field(default=None)
    inventory: AttrBlock = field(default=None)
    freight: AttrBlock = field(default=None)

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
