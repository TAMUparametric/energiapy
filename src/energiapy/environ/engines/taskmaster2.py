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
from ..report import Report
from ..task import Task2

act = {
    'ply': True,
    'csh': True,
    'res': True,
    'mat': True,
    'lnd': True,
    'pro': True,
    'stg': True,
    'trn': True,
    'loc': True,
    'lnk': True,
    'ntw': True,
}

emit = {
    'emn': True,
    'pro': True,
    'stg': True,
    'trn': True,
    'loc': True,
    'lnk': True,
    'ntw': True,
}

transact = {
    'csh': True,
}


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
        self.has = Task2(attr='has', var=Give, **act)
        self.needs = Task2(attr='needs', var=Take, **act)
        # Emission
        self.emit = Task2(attr='emit', var=Emit, **emit)
        self.emit = Task2(attr='abate', var=Emit, **emit)
        # Cash
        self.spend = Task2(
            attr='spend',
            csh=True,
            var=Spend,
        )
        self.earn = Task2(attr='earn', csh=True, var=Earn)
        # Land and Material (Used)
        self.use = Task2(attr='use', mat=True, lnd=True, var=Use)
        self.dispose = Task2(attr='dispose', mat=True, lnd=True, var=Use)
        # Resource
        self.buy = Task2(attr='buy', res=True, var=Buy, pro=True)
        self.sell = Task2(attr='sell', res=True, var=Sell, pro=True)
        self.ship = Task2(attr='ship', res=True, var=Ship, trn=True)
        # Operational
        self.capacity = Task2(
            attr='capacity', pro=True, stg=True, trn=True, var=Capacitate
        )
        # self.operate = Task2(
        #     attr='operate', pro= True, stg=True, trn = True, var=Operate
        # )
        # Process
        self.produce = Task2(attr='produce', pro=True, var=Operate)
        # Storage
        self.store = Task2(attr='store', stg=True, var=Operate)
        # Transit
        self.transport = Task2(attr='transport', trn=True, var=Operate)

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
class _Exacts(_TscExacts, _EmnExacts, _UseExacts, _LseExacts, _RteExacts):
    """These are Exact Component Inputs

    These are inherited across all Spatial Components
    if defined at Network

    There is no Network value for these

    """

    def __post_init__(self):
        # ---------Transacts---------
        # Resource
        self.buy_price = Task2(
            attr='buy_price',
            res=True,
            var=TransactBuy,
            pro=True,
        )
        self.sell_price = Task2(attr='sell_price', res=True, var=TransactSll, pro=True)
        self.credit = Task2(attr='credit', res=True, var=TransactCrd, pro=True)
        self.penalty = Task2(attr='penalty', res=True, var=TransactPnt, pro=True)
        # Land and Material (Used)
        self.use_cost = Task2(
            attr='use_cost', mat=True, lnd=True, var=TransactUse, pro=True
        )
        # Operational
        self.capex = Task2(
            attr='capex',
            pro=True,
            stg=True,
            trn=True,
            var=TransactStp,
            var_i=TransactStpI,
        )
        self.opex = Task2(
            attr='opex',
            pro=True,
            stg=True,
            trn=True,
            var=TransactOpr,
            var_i=TransactOprI,
        )

        # ---------Emissions---------
        # Resource
        self.buy_emission = Task2(attr='buy_emission', res=True, var=EmitBuy, pro=True)
        self.sell_emission = Task2(
            attr='sell_emission', res=True, var=EmitSll, pro=True
        )
        self.loss_emission = Task2(
            attr='loss_emission',
            res=True,
            var=EmitLse,
            stg=True,
            trn=True,
        )
        # Land and Material (Used)
        self.use_emission = Task2(attr='use_emission', mat=True, lnd=True, var=EmitUse)
        # Operational
        self.setup_emission = Task2(
            attr='setup_emission', pro=True, stg=True, trn=True, var=EmitStp
        )

        # ---------Uses---------
        # Operational
        self.setup_use = Task2(
            attr='setup_use', pro=True, stg=True, trn=True, var=UseStp
        )

        # ---------Losses---------
        # Storage Operation
        self.inventory_loss = Task2(attr='inventory_loss', stg=True, var=Lose)
        # Transit Operation
        self.freight_loss = Task2(attr='freight_loss', trn=True, var=Lose)
        # ---------Rates---------
        # Operational
        self.setup_time = Task2(attr='setup_time', pro=True, stg=True, trn=True)
        # Transit Operation
        self.speed = Task2(attr='speed', trn=True)

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
class _Balances(_ProBalance, _StgBalance, _TrnBalance):
    """These are Balances for Resources
    defined at Operational Components
    """

    def __post_init__(self):
        # Process
        self.conversion = Task2(attr='conversion', pro=True)
        # Storage
        self.inventory = Task2(attr='inventory', stg=True)
        # Transit
        self.freight = Task2(attr='freight', trn=True)

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
