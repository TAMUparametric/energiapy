""" This has three objects
Task: 
    individual attributes of Components
Reports:
    collections of Component attributes 
    this is helpful when Commodity attributes are declared at Operations
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
    _UseExacts,
)
from ...core._handy._dunders import _Dunders
from ..tasks.report import Report
from ..tasks.bound import Bound, BoundBound
from ..tasks.calculation import Calculation
from ..tasks.balancing import Balancing

from ...components.analytical.player import Player
from ...components.commodity.cash import Cash
from ...components.commodity.emission import Emission
from ...components.commodity.resource import Resource
from ...components.operation.process import Process
from ...components.operation.storage import Storage
from ...components.operation.transit import Transit
from ...components.operation._operation import _Operation
from ...components.commodity._used import _Used
from ...components.temporal.horizon import Horizon

from ...elements.parameters.balances.conversion import Conversion
from ...elements.parameters.balances.freight import Freight
from ...elements.parameters.balances.inventory import Inventory


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
        self.has = Bound(name='has', root=Player, p=True, varsym='give', prmsym='Has')
        self.needs = Bound(
            name='needs', root=Player, m=True, varsym='take', prmsym='Needs'
        )
        # Cash
        self.spend = Bound(
            name='spend', root=Cash, p=True, varsym='spend', prmsym='Spend'
        )
        self.earn = Bound(name='earn', root=Cash, m=True, varsym='earn', prmsym='Earn')
        # Emission
        self.emit = Bound(
            name='emit', root=Emission, p=True, varsym='emit', prmsym='Emit'
        )
        self.sequester = Bound(
            name='sequester',
            root=Emission,
            m=True,
            varsym='sequester',
            prmsym='Sequester',
        )
        # Material | Land
        self.use = Bound(name='use', root=_Used, p=True, varsym='use', prmsym='Use')
        self.dispose = Bound(
            name='dispose', root=_Used, m=True, varsym='dispose', prmsym='Dispose'
        )
        # Resource
        self.buy = Bound(name='buy', root=Resource, p=True, varsym='buy', prmsym='Buy')
        self.sell = Bound(
            name='sell', root=Resource, m=True, varsym='sell', prmsym='Sell'
        )
        self.ship = Bound(
            name='ship', root=Resource, p=True, varsym='ship', prmsym='Ship'
        )
        self.lose = Bound(
            name='lose', root=Resource, p=True, varsym='lose', prmsym='Lose'
        )
        # Operational
        self.setup = Bound(
            name='setup',
            root=_Operation,
            p=True,
            varsym='capacity^add',
            prmsym='Capacity^add',
        )
        self.dismantle = Bound(
            name='dismantle',
            root=_Operation,
            m=True,
            varsym='capacity^rmv',
            prmsym='Capacity^rmv',
        )
        # Process
        self.produce = BoundBound(
            name='produce',
            root=Process,
            varsym='produce',
            parent=self.setup,
            prmsym='Cap^F',
        )
        # Storage
        self.store = BoundBound(
            name='store',
            root=Storage,
            varsym='store',
            parent=self.setup,
            prmsym='Cap^F',
        )
        # Transit
        self.transport = BoundBound(
            name='transport',
            root=Transit,
            varsym='transport',
            parent=self.setup,
            prmsym='Cap^F',
        )

    @staticmethod
    def bounds():
        """Returns all Bounds"""

        return sum(
            [
                [f.name for f in fields(bnds)]
                for bnds in [
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
class _Exacts(_Bounds, _TscExacts, _EmnExacts, _UseExacts, _LseExacts, _RteExacts):
    """These are Exact Component Inputs

    These are inherited across all Spatial Components
    if defined at Network

    There is no Network value for these

    """

    def __post_init__(self):
        _Bounds.__post_init__(self)
        # ---------Transacts---------
        # Resource
        self.buy_price = Calculation(
            name='buy_price',
            root=Cash,
            varsym='exp^buy',
            parent=self.buy,
            prmsym='Price^buy',
        )
        self.sell_price = Calculation(
            name='sell_price',
            root=Cash,
            varsym='exp^sell',
            parent=self.sell,
            prmsym='Price^sell',
        )
        self.credit = Calculation(
            name='credit',
            root=Cash,
            varsym='exp^credit',
            parent=self.sell,
            prmsym='Credit',
        )
        self.penalty = Calculation(
            name='penalty',
            root=Cash,
            varsym='exp^penalty',
            parent=self.sell,
            prmsym='Penalty',
        )
        # Land and Material (Used)
        self.use_cost = Calculation(
            name='use_cost',
            root=Cash,
            varsym='exp^use',
            parent=self.use,
            prmsym='Cost^use',
        )
        self.dispose_cost = Calculation(
            name='dispose_cost',
            root=Cash,
            varsym='exp^dsp',
            parent=self.dispose,
            prmsym='Cost^dsp',
        )
        # Operational
        self.capex = Calculation(
            name='capex',
            root=Cash,
            varsym='exp^capex',
            parent=self.setup,
            prmsym='Capex',
        )
        self.opex = Calculation(
            name='opex',
            root=Cash,
            varsym='exp^opex',
            parent=self.produce,
            prmsym='Opex',
        )
        # ---------Emissions---------
        # Resource
        self.buy_emit = Calculation(
            name='buy_emit',
            root=Emission,
            varsym='emit^buy',
            parent=self.buy,
            prmsym='Emit^buy',
        )
        self.buy_sequester = Calculation(
            name='buy_sequester',
            root=Emission,
            varsym='sequester^buy',
            parent=self.buy,
            prmsym='Sequester^buy',
        )
        self.sell_emit = Calculation(
            name='sell_emit',
            root=Emission,
            varsym='emit^sell',
            parent=self.sell,
            prmsym='Emit^sell',
        )
        self.sell_sequester = Calculation(
            name='sell_sequester',
            root=Emission,
            varsym='sequester^sell',
            parent=self.sell,
            prmsym='Sequester^sell',
        )
        self.lose_emit = Calculation(
            name='lose_emit',
            root=Emission,
            varsym='emit^lose',
            parent=self.lose,
            prmsym='Emit^lose',
        )
        # Land and Material (Used)
        self.use_emit = Calculation(
            name='use_emit',
            root=Emission,
            varsym='emit^use',
            parent=self.use,
            prmsym='Emit^use',
        )
        self.use_sequester = Calculation(
            name='use_sequester',
            root=Emission,
            varsym='sequester^use',
            parent=self.use,
            prmsym='Sequester^use',
        )
        self.dispose_emit = Calculation(
            name='dispose_emit',
            root=Emission,
            varsym='emit^dispose',
            parent=self.dispose,
            prmsym='Emit^dispose',
        )
        # Operational
        self.setup_emit = Calculation(
            name='setup_emit',
            root=Emission,
            varsym='emit^setup',
            parent=self.setup,
            prmsym='Emit^setup',
        )
        self.setup_sequester = Calculation(
            name='setup_sequester',
            root=Emission,
            varsym='sequester^setup',
            parent=self.setup,
            prmsym='Sequester^setup',
        )
        self.dismantle_emit = Calculation(
            name='dismantle_emit',
            root=Emission,
            varsym='emit^dismantle',
            parent=self.dismantle,
            prmsym='Emit^dismantle',
        )
        # ---------Uses---------
        # Operational
        self.setup_use = Calculation(
            name='setup_use',
            root=_Used,
            varsym='use^setup',
            parent=self.setup,
            prmsym='Use^setup',
        )
        # ---------Losses---------
        # Storage Operation
        self.inventory_loss = Calculation(
            name='inventory_loss',
            root=Resource,
            varsym='lose^stg',
            parent=self.store,
            prmsym='Loss^stg',
        )
        # Transit Operation
        self.freight_loss = Calculation(
            name='freight_loss',
            root=Resource,
            varsym='lose^trn',
            parent=self.transport,
            prmsym='Loss^trn',
        )
        # ---------Rates---------
        # Operational
        self.setup_time = Calculation(
            name='setup_time',
            root=Horizon,
            varsym='time^setup',
            parent=self.setup,
            prmsym='τ',
        )
        # Transit Operation
        self.speed = Calculation(
            name='speed',
            root=Horizon,
            varsym='speed',
            parent=self.transport,
            prmsym='Speed',
        )

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
        return [f.name for f in fields(_UseExacts)]

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
                    _UseExacts,
                    _LseExacts,
                ]
            ],
            [],
        )


@dataclass
class _Balances(_Exacts, _ProBalance, _StgBalance, _TrnBalance):
    """These are Balances for Resources
    defined at Operational Components
    """

    def __post_init__(self):
        _Exacts.__post_init__(self)
        # Process
        self.conversion = Balancing(
            name='conversion',
            opn=Process,
            balance=Conversion,
            prmsym='η',
            parent=self.produce,
        )
        # Storage
        self.inventory = Balancing(
            name='inventory',
            opn=Storage,
            balance=Inventory,
            prmsym='φ',
            parent=self.store,
        )
        # Transit
        self.freight = Balancing(
            name='freight',
            opn=Transit,
            balance=Freight,
            prmsym='ψ',
            parent=self.transport,
        )

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
class Chanakya(_Balances, _Dunders):
    """This object collects all the attributes defined
    and makes a list of Indexs they are defined at

    """

    name: str = field(default=None)

    def __post_init__(self):
        self.name = f'TaskMaster|{self.name}|'
        _Balances.__post_init__(self)

    @property
    def report_transactions(self):
        """Collection of Transacts"""
        return Report(
            name='transactions',
            tasks=[getattr(self, attr) for attr in self.transactions()],
        )

    @property
    def report_uses(self):
        """Collection of Uses"""
        return Report(
            name='uses',
            tasks=[getattr(self, attr) for attr in self.uses()],
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
