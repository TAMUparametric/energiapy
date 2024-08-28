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

from ..attrs.balances import ProBalance, StgBalance, TrnBalance
from ..attrs.bounds import (
    PlyBounds,
    CshBounds,
    EmnBounds,
    UsedBounds,
    ResBounds,
    OpnBounds,
)
from ..attrs.exacts import ExpExacts, EmnExacts, UsgExacts, LssExacts, RteExacts

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
class AttrBounds(PlyBounds, CshBounds, EmnBounds, UsedBounds, ResBounds, OpnBounds):
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

    @classmethod
    def bounds(cls):
        """Returns all Bounds"""
        return fields(cls)


@dataclass
class AttrExacts(ExpExacts, EmnExacts, UsgExacts, LssExacts, RteExacts):
    """These are Exact Component Inputs

    These are inherited across all Spatial Components
    if defined at Network

    There is no Network value for these

    """

    def __post_init__(self):
        # ---------Expenses---------
        # Resource
        self.price_buy = AttrBlock(name='price_buy', cmp=[Resource])
        self.price_sell = AttrBlock(name='price_sell', cmp=[Resource])
        self.credit = AttrBlock(name='credit', cmp=[Resource])
        self.penalty = AttrBlock(name='penalty', cmp=[Resource])
        # Land and Material (Used)
        self.cost_use = AttrBlock(name='cost_use', cmp=[Land, Material])
        # Operational
        self.capex = AttrBlock(name='capex', cmp=[Process, Storage, Transit])
        self.opex = AttrBlock(name='opex', cmp=[Process, Storage, Transit])
        # ---------Emissions---------
        # Resource
        self.emission_buy = AttrBlock(name='emission_buy', cmp=[Resource])
        self.emission_sell = AttrBlock(name='emission_sell', cmp=[Resource])
        self.emission_loss = AttrBlock(name='emission_loss', cmp=[Resource])
        # Land and Material (Used)
        self.emission_use = AttrBlock(name='emission_use', cmp=[Land, Material])
        # Operational
        self.emission_setup = AttrBlock(
            name='emission_setup', cmp=[Process, Storage, Transit]
        )
        # ---------Uses---------
        # Operational
        self.use_land = AttrBlock(name='use_land', cmp=[Process, Storage, Transit])
        self.use_material = AttrBlock(
            name='use_material', cmp=[Process, Storage, Transit]
        )
        # ---------Losses---------
        # Storage Operation
        self.loss_storage = AttrBlock(name='loss_storage', cmp=[Storage])
        # Transit Operation
        self.loss_transit = AttrBlock(name='loss_transit', cmp=[Transit])
        # ---------Rates---------
        # Transit Operation
        self.speed = AttrBlock(name='speed', cmp=[Transit])

    @staticmethod
    def expenses():
        """Expenses"""
        return fields(ExpExacts)

    @staticmethod
    def emissions():
        """Emissions"""
        return fields(EmnExacts)

    @staticmethod
    def uses():
        """Uses"""
        return fields(UsgExacts)

    @staticmethod
    def losses():
        """Losses"""
        return fields(LssExacts)

    @staticmethod
    def rates():
        """Rates"""
        return fields(RteExacts)

    @classmethod
    def exacts(cls):
        """Returns all Exact Inputs"""
        return fields(cls)


@dataclass
class AttrBalances(ProBalance, StgBalance, TrnBalance):
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

    @classmethod
    def balances(cls):
        """Returns all Balances"""
        return fields(cls)


@dataclass
class Attr(AttrBounds, AttrExacts, AttrBalances, _Dunders):
    """This object collects all the attributes defined
    and makes a list of Dispositions they are defined at

    """

    name: str = field(default=None)

    def __post_init__(self):
        self.name = f'Attr|{self.name}|'
        AttrBounds.__post_init__(self)
        AttrExacts.__post_init__(self)
        AttrBalances.__post_init__(self)

    @property
    def coll_expenses(self):
        """Collection of Expenses"""
        return AttrCollection(
            name='expenses',
            attrblocks=[getattr(self, attr) for attr in self.expenses()],
        )

    @property
    def coll_uses_land(self):
        """Collection of Uses Land"""
        return AttrCollection(
            name='uses_land',
            attrblocks=[getattr(self, 'use_land')],
        )

    @property
    def coll_emissions(self):
        """Collection of Emissions"""
        return AttrCollection(
            name='emissions',
            attrblocks=[getattr(self, attr) for attr in self.emissions()],
        )

    @property
    def coll_losses(self):
        """Collection of Losses"""
        return AttrCollection(
            name='losses', attrblocks=[getattr(self, attr) for attr in self.losses()]
        )

    @property
    def coll_uses_material(self):
        """Collection of Uses Material"""
        return AttrCollection(
            name='uses_material',
            attrblocks=[getattr(self, 'use_material')],
        )
