""" This has three objects
AttrBlock: 
    individual attributes of Components
AttrCollections:
    collections of Component attributes 
    this is helpful when component attributes are declared at other Components
Attr: 
    Consists of: AttrBounds, AttrExacts, AttrBalances
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
    ProBounds,
    StgBounds,
    TrnBounds,
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

from ..variables.action import Give, Take
from ..variables.capacitate import Capacity
from ..variables.emit import EmitBuy, EmitSetUp, EmitLoss, EmitSell, Emit, EmitUse
from ..variables.expense import (
    Credit,
    Earn,
    ExpBuy,
    ExpSetUp,
    ExpSetUpI,
    ExpOpr,
    ExpOprI,
    ExpSell,
    ExpUsage,
    Penalty,
    Spend,
)
from ..variables.loss import Loss
from ..variables.operate import Operate
from ..variables.trade import Buy, Sell, Ship
from ..variables.use import Use, Usage


if TYPE_CHECKING:
    from ..core.aliases.is_component import IsComponent
    from ..core.aliases.is_variable import IsVariable


@dataclass
class AttrBlock(_Dunders):
    """Attr Block
    Handles the attributes of components
    Defines strict behaviour

    Attributes:
        name (str): The name of the attribute block
        root (List[IsComponent]): List of Components where the attribute can be declared
        other (List[IsComponent]): List of Incongruent Components where the Component attribute can be declared
        task (IsVariable): Task Variable
        task_i (IsVariable): Incidental Task Variable

    """

    name: str = field(default=None)
    root: List[IsComponent] = field(default_factory=list)
    other: List[IsComponent] = field(default_factory=list)
    task: IsVariable = field(default=None)
    task_i: IsVariable = field(default=None)

    def __post_init__(self):
        self.name = f'Attr|{self.name}|'
        # Elements associated with the attribute
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
        attrblocks (List[AttrBlock]): List of AttrBlocks that the collection consists of
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
class AttrBounds(
    PlyBounds,
    CshBounds,
    EmnBounds,
    UsedBounds,
    ResBounds,
    OpnBounds,
    ProBounds,
    StgBounds,
    TrnBounds,
):
    """These are Bounds for the Components

    Bounds can be different for Network and individual Spatial Components
    """

    def __post_init__(self):
        # Player
        self.has = AttrBlock(name='has', root=[Player], task=Give)
        self.needs = AttrBlock(name='needs', root=[Player], task=Take)
        # Cash
        self.spend = AttrBlock(name='spend', root=[Cash], task=Spend)
        self.earn = AttrBlock(name='earn', root=[Cash], task=Earn)
        # Emission
        self.emit = AttrBlock(name='emit', root=[Emission], task=Emit)
        # Land and Material (Used)
        self.use = AttrBlock(name='use', root=[Land, Material], task=Use)
        # Resource
        self.buy = AttrBlock(name='buy', root=[Resource], task=Buy, other=[Process])
        self.sell = AttrBlock(name='sell', root=[Resource], task=Sell, other=[Process])
        self.ship = AttrBlock(name='ship', root=[Resource], task=Ship, other=[Transit])
        # Operational
        self.capacity = AttrBlock(
            name='capacity', root=[Process, Storage, Transit], task=Capacity
        )
        self.operate = AttrBlock(
            name='operate', root=[Process, Storage, Transit], task=Operate
        )
        # # Process
        # self.produce = AttrBlock(name='produce', root=[Process])
        # # Storage
        # self.store = AttrBlock(name='store', root=[Storage])
        # # Transit
        # self.transport = AttrBlock(name='transport', root=[Transit])

    @staticmethod
    def bounds():
        """Returns all Bounds"""

        return sum(
            [
                [f.name for f in fields(bln)]
                for bln in [
                    PlyBounds,
                    CshBounds,
                    EmnBounds,
                    UsedBounds,
                    ResBounds,
                    OpnBounds,
                    ProBounds,
                    StgBounds,
                    TrnBounds,
                ]
            ],
            [],
        )


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
        self.price_buy = AttrBlock(
            name='price_buy',
            root=[Resource],
            task=ExpBuy,
        )
        self.price_sell = AttrBlock(name='price_sell', root=[Resource], task=ExpSell)
        self.credit = AttrBlock(name='credit', root=[Resource], task=Credit)
        self.penalty = AttrBlock(name='penalty', root=[Resource], task=Penalty)
        # Land and Material (Used)
        self.cost_use = AttrBlock(
            name='cost_use', root=[Land, Material], task=ExpUsage, other=[Process]
        )
        # Operational
        self.capex = AttrBlock(
            name='capex',
            root=[Process, Storage, Transit],
            task=ExpSetUp,
            task_i=ExpSetUpI,
        )
        self.opex = AttrBlock(
            name='opex', root=[Process, Storage, Transit], task=ExpOpr, task_i=ExpOprI
        )
        # ---------Emissions---------
        # Resource
        self.emission_buy = AttrBlock(
            name='emission_buy', root=[Resource], task=EmitBuy, other=[Process]
        )
        self.emission_sell = AttrBlock(
            name='emission_sell', root=[Resource], task=EmitSell, other=[Process]
        )
        self.emission_loss = AttrBlock(
            name='emission_loss',
            root=[Resource],
            task=EmitLoss,
            other=[Storage, Transit],
        )
        # Land and Material (Used)
        self.emission_use = AttrBlock(
            name='emission_use', root=[Land, Material], task=EmitUse
        )
        # Operational
        self.emission_setup = AttrBlock(
            name='emission_setup', root=[Process, Storage, Transit], task=EmitSetUp
        )
        # ---------Uses---------
        # Operational
        self.use_land = AttrBlock(
            name='use_land', root=[Process, Storage, Transit], task=Usage
        )
        self.use_material = AttrBlock(
            name='use_material', root=[Process, Storage, Transit], task=Usage
        )
        # ---------Losses---------
        # Storage Operation
        self.loss_storage = AttrBlock(name='loss_storage', root=[Storage], task=Loss)
        # Transit Operation
        self.loss_transit = AttrBlock(name='loss_transit', root=[Transit], task=Loss)
        # ---------Rates---------
        # Operational
        self.setup_time = AttrBlock(name='setup_time', root=[Process, Storage, Transit])
        # Transit Operation
        self.speed = AttrBlock(name='speed', root=[Transit])

    @staticmethod
    def expenses():
        """Expenses"""
        return [f.name for f in fields(ExpExacts)]

    @staticmethod
    def emissions():
        """Emissions"""
        return [f.name for f in fields(EmnExacts)]

    @staticmethod
    def usages():
        """Uses"""
        return [f.name for f in fields(UsgExacts)]

    @staticmethod
    def losses():
        """Losses"""
        return [f.name for f in fields(LssExacts)]

    @staticmethod
    def rates():
        """Rates"""
        return [f.name for f in fields(RteExacts)]

    @staticmethod
    def exacts():
        """Returns all Exact Inputs"""
        return sum(
            [
                [f.name for f in fields(ext)]
                for ext in [ExpExacts, EmnExacts, UsgExacts, LssExacts]
            ],
            [],
        )


@dataclass
class AttrBalances(ProBalance, StgBalance, TrnBalance):
    """These are Balances for Resources
    defined at Operational Components
    """

    def __post_init__(self):
        # Process
        self.conversion = AttrBlock(name='conversion', root=[Process])
        # Storage
        self.inventory = AttrBlock(name='inventory', root=[Storage])
        # Transit
        self.freight = AttrBlock(name='freight', root=[Transit])

    @staticmethod
    def balances():
        """Returns all Balances"""
        return sum(
            [
                [f.name for f in fields(bln)]
                for bln in [ProBalance, StgBalance, TrnBalance]
            ],
            [],
        )


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
