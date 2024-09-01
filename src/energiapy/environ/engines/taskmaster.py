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

from dataclasses import asdict, dataclass, field, fields

from ...components._attrs._balances import _ProBalance, _StgBalance, _TrnBalance
from ...components._attrs._bounds import (
    _CshBounds,
    _EmnBounds,
    _OpnBounds,
    _PlyBounds,
    _ProBounds,
    _ResBounds,
    _StgBounds,
    _TrnBounds,
    _UsdBounds,
)
from ...components._attrs._exacts import (
    _EmnExacts,
    _LseExacts,
    _RteExacts,
    _TscExacts,
    _UsdExacts,
    _OpnUsdExacts,
)
from ...components.analytical.player import Player
from ...components.commodity.cash import Cash
from ...components.commodity.emission import Emission
from ...components.commodity.land import Land
from ...components.commodity.material import Material
from ...components.commodity.resource import Resource
from ...components.operation.process import Process
from ...components.operation.storage import Storage
from ...components.operation.transit import Transit
from ...core._handy._dunders import _Dunders
from ...core._handy._printers import _Print
from ...core.aliases.cmps.isdfn import IsDfn
from ...core.aliases.elms.isvar import IsVar
from ...elements.variables.act import Give, Take
from ...elements.variables.emit import Emit, EmitBuy, EmitLse, EmitSll, EmitStp, EmitUse
from ...elements.variables.lose import Lose
from ...elements.variables.operate import Operate
from ...elements.variables.setup import Capacitate
from ...elements.variables.trade import Buy, Sell, Ship
from ...elements.variables.transact import (
    Earn,
    Spend,
    TransactBuy,
    TransactCrd,
    TransactOpr,
    TransactOprI,
    TransactPnt,
    TransactSll,
    TransactStp,
    TransactStpI,
    TransactUse,
)
from ...elements.variables.use import Use, UseStp


class _TskPrint(_Print):
    """Prints Task"""

    def eqns(self):
        """Prints all equations in the ProgramBlock"""
        for constraint in getattr(self, 'constraints'):
            yield constraint.equation


@dataclass
class Task(_Dunders, _TskPrint):
    """Task
    Handles the attributes of components
    Defines strict behaviour

    Attributes:
        attr (str): attr associated with Task
        root (list[IsDfn]): list of Components where the attribute can be declared
        other (list[IsDfn]): list of Incongruent Components where the Component attribute can be declared
        var (IsVar): Task Variable
        var_i (IsVar): Incidental Task Variable
        spt (list[IsSpt]): list of Spatial Components where the attribute can be declared

    """

    attr: str = field(default=None)
    root: list[IsDfn] = field(default_factory=list)
    other: list[IsDfn] = field(default_factory=list)
    var: IsVar = field(default=None)
    var_i: IsVar = field(default=None)

    def __post_init__(self):
        self.name = f'Task|{self.attr}|'
        # Elements associated with the attribute
        self.values = []
        self.parameters = []
        self.constraints = []
        self.variables = []
        self.indices = []


@dataclass
class Report(_Dunders, _TskPrint):
    """Task is a collection of Tasks

    Taskibutes:
        name (str): The name of the attribute collection
        tasks (list[Task]): list of TaskBlocks that the collection consists of
    """

    name: str = field(default=None)
    tasks: list[Task] = field(default_factory=list)

    def __post_init__(self):
        self.name = f'Report|{self.name}|'
        # Report associated with the attribute
        self.values = sum([attr.values for attr in self.tasks], [])
        self.parameters = sum([attr.parameters for attr in self.tasks], [])
        self.indices = sum([attr.indices for attr in self.tasks], [])
        self.constraints = sum([attr.constraints for attr in self.tasks], [])
        self.variables = sum([attr.variables for attr in self.tasks], [])


@dataclass
class _Bounds(
    _PlyBounds,
    _CshBounds,
    _EmnBounds,
    _UsdBounds,
    _ResBounds,
    _OpnBounds,
    _ProBounds,
    _StgBounds,
    _TrnBounds,
):
    """These are Bounds for the Components

    Bounds can be different for Network and individual Spatial Components
    """

    def __post_init__(self):
        # Player
        self.has = Task(attr='has', root=[Player], var=Give)
        self.needs = Task(attr='needs', root=[Player], var=Take)
        # Cash
        self.spend = Task(attr='spend', root=[Cash], var=Spend)
        self.earn = Task(attr='earn', root=[Cash], var=Earn)
        # Emission
        self.emit = Task(attr='emit', root=[Emission], var=Emit)
        # Land and Material (Used)
        self.use = Task(attr='use', root=[Land, Material], var=Use)
        # Resource
        self.buy = Task(attr='buy', root=[Resource], var=Buy, other=[Process])
        self.sell = Task(attr='sell', root=[Resource], var=Sell, other=[Process])
        self.ship = Task(attr='ship', root=[Resource], var=Ship, other=[Transit])
        # Operational
        self.capacity = Task(
            attr='capacity', root=[Process, Storage, Transit], var=Capacitate
        )
        # self.operate = Task(
        #     attr='operate', root=[Process, Storage, Transit], var=Operate
        # )
        # Process
        self.produce = Task(attr='produce', root=[Process], var=Operate)
        # Storage
        self.store = Task(attr='store', root=[Storage], var=Operate)
        # Transit
        self.transport = Task(attr='transport', root=[Transit], var=Operate)

    @staticmethod
    def bounds():
        """Returns all Bounds"""

        return sum(
            [
                [f.name for f in fields(bln)]
                for bln in [
                    _PlyBounds,
                    _CshBounds,
                    _EmnBounds,
                    _UsdBounds,
                    _ResBounds,
                    _OpnBounds,
                    _ProBounds,
                    _StgBounds,
                    _TrnBounds,
                ]
            ],
            [],
        )


@dataclass
class _Exacts(
    _TscExacts, _EmnExacts, _UsdExacts, _OpnUsdExacts, _LseExacts, _RteExacts
):
    """These are Exact Component Inputs

    These are inherited across all Spatial Components
    if defined at Network

    There is no Network value for these

    """

    def __post_init__(self):
        # ---------Transacts---------
        # Resource
        self.buy_price = Task(
            attr='buy_price',
            root=[Resource],
            var=TransactBuy,
            other=[Process],
        )
        self.sell_price = Task(
            attr='sell_price', root=[Resource], var=TransactSll, other=[Process]
        )
        self.credit = Task(
            attr='credit', root=[Resource], var=TransactCrd, other=[Process]
        )
        self.penalty = Task(
            attr='penalty', root=[Resource], var=TransactPnt, other=[Process]
        )
        # Land and Material (Used)
        self.use_cost = Task(
            attr='use_cost', root=[Land, Material], var=TransactUse, other=[Process]
        )
        # Operational
        self.capex = Task(
            attr='capex',
            root=[Process, Storage, Transit],
            var=TransactStp,
            var_i=TransactStpI,
        )
        self.opex = Task(
            attr='opex',
            root=[Process, Storage, Transit],
            var=TransactOpr,
            var_i=TransactOprI,
        )

        self.land_use_cost = Task(
            attr='land_use_cost', root=[Land], var=TransactUse, other=[Process]
        )

        self.material_use_cost = Task(
            attr='material_use_cost',
            root=[Material],
            var=TransactUse,
            other=[Process],
        )

        # ---------Emissions---------
        # Resource
        self.buy_emission = Task(
            attr='buy_emission', root=[Resource], var=EmitBuy, other=[Process]
        )
        self.sell_emission = Task(
            attr='sell_emission', root=[Resource], var=EmitSll, other=[Process]
        )
        self.loss_emission = Task(
            attr='loss_emission',
            root=[Resource],
            var=EmitLse,
            other=[Storage, Transit],
        )
        # Land and Material (Used)
        self.use_emission = Task(
            attr='use_emission', root=[Land, Material], var=EmitUse
        )
        # Operational
        self.setup_emission = Task(
            attr='setup_emission', root=[Process, Storage, Transit], var=EmitStp
        )
        self.land_use_emission = Task(
            attr='land_use_emission',
            root=[Land],
            other=[Process, Storage, Transit],
            var=EmitUse,
        )
        self.material_use_emission = Task(
            attr='material_use_emission',
            root=[Material],
            other=[Process, Storage, Transit],
            var=EmitUse,
        )
        # ---------Uses---------
        # Operational
        self.land_use = Task(
            attr='land_use', root=[Process, Storage, Transit], var=UseStp
        )
        self.material_use = Task(
            attr='material_use', root=[Process, Storage, Transit], var=UseStp
        )
        # ---------Losses---------
        # Storage Operation
        self.inventory_loss = Task(attr='inventory_loss', root=[Storage], var=Lose)
        # Transit Operation
        self.freight_loss = Task(attr='freight_loss', root=[Transit], var=Lose)
        # ---------Rates---------
        # Operational
        self.setup_time = Task(attr='setup_time', root=[Process, Storage, Transit])
        # Transit Operation
        self.speed = Task(attr='speed', root=[Transit])

    @staticmethod
    def transactions():
        """Transacts"""
        return [f.name for f in fields(_TscExacts)]

    @staticmethod
    def emissions():
        """Emissions"""
        return [f.name for f in fields(_EmnExacts)]

    @staticmethod
    def uses():
        """Uses"""
        return [f.name for f in fields(_UsdExacts) + fields(_OpnUsdExacts)]

    @staticmethod
    def losses():
        """Losses"""
        return [f.name for f in fields(_LseExacts)]

    @staticmethod
    def rates():
        """Rates"""
        return [f.name for f in fields(_RteExacts)]

    @staticmethod
    def exacts():
        """Returns all Exact Inputs"""
        return sum(
            [
                [f.name for f in fields(ext)]
                for ext in [
                    _TscExacts,
                    _EmnExacts,
                    _UsdExacts,
                    _OpnUsdExacts,
                    _LseExacts,
                ]
            ],
            [],
        )


@dataclass
class _Balances(_ProBalance, _StgBalance, _TrnBalance):
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
                for bln in [_ProBalance, _StgBalance, _TrnBalance]
            ],
            [],
        )


@dataclass
class Chanakya(_Balances, _Bounds, _Exacts, _Dunders):
    """This object collects all the attributes defined
    and makes a list of Indexs they are defined at

    """

    name: str = field(default=None)

    def __post_init__(self):
        self.name = f'TaskMaster|{self.name}|'
        _Balances.__post_init__(self)
        _Bounds.__post_init__(self)
        _Exacts.__post_init__(self)

    @property
    def report_transactions(self):
        """Collection of Transacts"""
        return Report(
            name='transactions',
            tasks=[getattr(self, attr) for attr in self.transactions()],
        )

    @property
    def report_uses_land(self):
        """Collection of Uses Land"""
        return Report(
            name='uses_land',
            tasks=[getattr(self, 'land_use')],
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
            tasks=[getattr(self, 'material_use')],
        )

    def vars(self):
        """Returns all Variables"""
        return sorted(
            {
                i['var']
                for i in list(asdict(self).values())
                if isinstance(i, dict) and i['var']
            }
            | {
                i['var_i']
                for i in list(asdict(self).values())
                if isinstance(i, dict) and i['var_i']
            },
            key=lambda x: x.cname(),
        )