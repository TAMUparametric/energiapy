""" This has three objects
Task: 
    individual attributes of Components
Reports:
    collections of Component attributes 
    this is helpful when component attributes are declared at other Components
Task: 
    Consists of: Bounds, Exacts, TaskBalances
    All TaskBlocks, there is only one instance of this in the Scenario
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
class Task(_Dunders):
    """Task
    Handles the attributes of components
    Defines strict behaviour

    Attributes:
        attr (str): attr associated with Task
        root (List[IsComponent]): List of Components where the attribute can be declared
        other (List[IsComponent]): List of Incongruent Components where the Component attribute can be declared
        task (IsVariable): Task Variable
        task_i (IsVariable): Incidental Task Variable
        spt (List[IsSpatial]): List of Spatial Components where the attribute can be declared

    """

    attr: str = field(default=None)
    root: List[IsComponent] = field(default_factory=list)
    other: List[IsComponent] = field(default_factory=list)
    task: IsVariable = field(default=None)
    task_i: IsVariable = field(default=None)

    def __post_init__(self):
        self.name = f'Task|{self.attr}|'
        # Elements associated with the attribute
        self.values = []
        self.parameters = []
        self.constraints = []
        self.variables = []
        self.dispositions = []


@dataclass
class Report(_Dunders):
    """Task is a collection of Tasks

    Taskibutes:
        name (str): The name of the attribute collection
        tasks (List[Task]): List of TaskBlocks that the collection consists of
    """

    name: str = field(default=None)
    tasks: List[Task] = field(default_factory=list)

    def __post_init__(self):
        self.name = f'Report|{self.name}|'
        # Report associated with the attribute
        self.values = sum([attr.values for attr in self.tasks], [])
        self.parameters = sum([attr.parameters for attr in self.tasks], [])
        self.dispositions = sum([attr.dispositions for attr in self.tasks], [])
        self.constraints = sum([attr.constraints for attr in self.tasks], [])
        self.variables = sum([attr.variables for attr in self.tasks], [])


@dataclass
class _Bounds(
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
        self.has = Task(attr='has', root=[Player], task=Give)
        self.needs = Task(attr='needs', root=[Player], task=Take)
        # Cash
        self.spend = Task(attr='spend', root=[Cash], task=Spend)
        self.earn = Task(attr='earn', root=[Cash], task=Earn)
        # Emission
        self.emit = Task(attr='emit', root=[Emission], task=Emit)
        # Land and Material (Used)
        self.use = Task(attr='use', root=[Land, Material], task=Use)
        # Resource
        self.buy = Task(attr='buy', root=[Resource], task=Buy, other=[Process])
        self.sell = Task(attr='sell', root=[Resource], task=Sell, other=[Process])
        self.ship = Task(attr='ship', root=[Resource], task=Ship, other=[Transit])
        # Operational
        self.capacity = Task(
            attr='capacity', root=[Process, Storage, Transit], task=Capacity
        )
        # self.operate = Task(
        #     attr='operate', root=[Process, Storage, Transit], task=Operate
        # )
        # Process
        self.produce = Task(attr='produce', root=[Process], task=Operate)
        # Storage
        self.store = Task(attr='store', root=[Storage], task=Operate)
        # Transit
        self.transport = Task(attr='transport', root=[Transit], task=Operate)

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
class _Exacts(ExpExacts, EmnExacts, UsgExacts, LssExacts, RteExacts):
    """These are Exact Component Inputs

    These are inherited across all Spatial Components
    if defined at Network

    There is no Network value for these

    """

    def __post_init__(self):
        # ---------Expenses---------
        # Resource
        self.price_buy = Task(
            attr='price_buy',
            root=[Resource],
            task=ExpBuy,
            other=[Process],
        )
        self.price_sell = Task(
            attr='price_sell', root=[Resource], task=ExpSell, other=[Process]
        )
        self.credit = Task(attr='credit', root=[Resource], task=Credit, other=[Process])
        self.penalty = Task(
            attr='penalty', root=[Resource], task=Penalty, other=[Process]
        )
        # Land and Material (Used)
        self.cost_use = Task(
            attr='cost_use', root=[Land, Material], task=ExpUsage, other=[Process]
        )
        # Operational
        self.capex = Task(
            attr='capex',
            root=[Process, Storage, Transit],
            task=ExpSetUp,
            task_i=ExpSetUpI,
        )
        self.opex = Task(
            attr='opex', root=[Process, Storage, Transit], task=ExpOpr, task_i=ExpOprI
        )

        self.cost_use_land = Task(
            attr='cost_use_land', root=[Land], task=ExpUsage, other=[Process]
        )

        self.cost_use_material = Task(
            attr='cost_use_material',
            root=[Material],
            task=ExpUsage,
            other=[Process],
        )

        # ---------Emissions---------
        # Resource
        self.emission_buy = Task(
            attr='emission_buy', root=[Resource], task=EmitBuy, other=[Process]
        )
        self.emission_sell = Task(
            attr='emission_sell', root=[Resource], task=EmitSell, other=[Process]
        )
        self.emission_loss = Task(
            attr='emission_loss',
            root=[Resource],
            task=EmitLoss,
            other=[Storage, Transit],
        )
        # Land and Material (Used)
        self.emission_use = Task(
            attr='emission_use', root=[Land, Material], task=EmitUse
        )
        # Operational
        self.emission_setup = Task(
            attr='emission_setup', root=[Process, Storage, Transit], task=EmitSetUp
        )
        self.emission_use_land = Task(
            attr='emission_use_land',
            root=[Land],
            other=[Process, Storage, Transit],
            task=EmitUse,
        )
        self.emission_use_material = Task(
            attr='emission_use_material',
            root=[Material],
            other=[Process, Storage, Transit],
            task=EmitUse,
        )
        # ---------Uses---------
        # Operational
        self.use_land = Task(
            attr='use_land', root=[Process, Storage, Transit], task=Usage
        )
        self.use_material = Task(
            attr='use_material', root=[Process, Storage, Transit], task=Usage
        )
        # ---------Losses---------
        # Storage Operation
        self.loss_storage = Task(attr='loss_storage', root=[Storage], task=Loss)
        # Transit Operation
        self.loss_transit = Task(attr='loss_transit', root=[Transit], task=Loss)
        # ---------Rates---------
        # Operational
        self.setup_time = Task(attr='setup_time', root=[Process, Storage, Transit])
        # Transit Operation
        self.speed = Task(attr='speed', root=[Transit])

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
class _Balances(ProBalance, StgBalance, TrnBalance):
    """These are Balances for Resources
    defined at Operational Components
    """

    def __post_init__(self):
        # Process
        self.conversion = Task(attr='conversion', root=[Process])
        # Storage
        self.inventory = Task(attr='inventory', root=[Storage])
        # Transit
        self.freight = Task(attr='freight', root=[Transit])

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
class TaskMaster(_Balances, _Bounds, _Exacts, _Dunders):
    """This object collects all the attributes defined
    and makes a list of Dispositions they are defined at

    """

    name: str = field(default=None)

    def __post_init__(self):
        self.name = f'TaskMaster|{self.name}|'
        _Balances.__post_init__(self)
        _Bounds.__post_init__(self)
        _Exacts.__post_init__(self)

    @property
    def report_expenses(self):
        """Collection of Expenses"""
        return Report(
            name='expenses',
            tasks=[getattr(self, attr) for attr in self.expenses()],
        )

    @property
    def report_uses_land(self):
        """Collection of Uses Land"""
        return Report(
            name='uses_land',
            tasks=[getattr(self, 'use_land')],
        )

    @property
    def report_emissions(self):
        """Collection of Emissions"""
        return Report(
            name='emissions',
            tasks=[getattr(self, attr) for attr in self.emissions()],
        )

    @property
    def report_losses(self):
        """Collection of Losses"""
        return Report(
            name='losses', tasks=[getattr(self, attr) for attr in self.losses()]
        )

    @property
    def report_uses_material(self):
        """Collection of Uses Material"""
        return Report(
            name='uses_material',
            tasks=[getattr(self, 'use_material')],
        )
