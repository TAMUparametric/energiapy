"""Task Master relates attributes to Elements
"""

from dataclasses import asdict, dataclass, field

from ...components._attrs._balances import _BalanceAttrs
from ...components._attrs._bounds import _BoundAttrs
from ...components._attrs._boundbounds import _BoundBoundAttrs
from ...components._attrs._exacts import _ExactAttrs
from ...core._handy._dunders import _Dunders
from ...elements.constraints.report import Report
from ...elements.constraints.bound import Bound
from ...elements.constraints.boundbound import BoundBound
from ...elements.constraints.calculate import Calculate
from ...elements.constraints.balance import Balance
from ...elements.constraints.lag import Lag

# from ...components.analytical.player import Player
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
class Chanakya(_BoundAttrs, _BoundBoundAttrs, _ExactAttrs, _BalanceAttrs, _Dunders):
    """This object collects all the attributes defined
    and makes a list of Indexs they are defined at

    """

    name: str = field(default=None)

    def __post_init__(self):
        self.name = f'TaskMaster|{self.name}|'
        # ---------Bounds-------------------------
        # ----------------------------------------
        # # Player
        # self.has = Bound(name='has', root=Player, p=True, varsym='give', prmsym='Has')
        # self.needs = Bound(
        #     name='needs', root=Player, m=True, varsym='take', prmsym='Needs'
        # )
        # Cash
        self.spend = Bound(attr='spend', root=Cash, p=True)
        self.earn = Bound(attr='earn', root=Cash, m=True)
        # Emission
        self.emit = Bound(attr='emit', root=Emission, p=True)
        self.sequester = Bound(attr='sequester', root=Emission, m=True)
        # Material | Land
        self.use = Bound(attr='use', root=_Used, p=True)
        self.dispose = Bound(attr='dispose', root=_Used, m=True)
        # Resource
        self.buy = Bound(attr='buy', root=Resource, p=True)
        self.sell = Bound(attr='sell', root=Resource, m=True)
        self.ship = Bound(attr='ship', root=Resource, p=True)
        self.lose = Bound(attr='lose', root=Resource, p=True)
        self.recover = Bound(attr='recover', root=Resource, m=True)

        # Operational
        self.setup = Bound(attr='setup', root=_Operation, p=True)
        self.dismantle = Bound(attr='dismantle', root=_Operation, m=True)

        # ----------BoundBounds-----------
        # ----------------------------------------

        self.operate = BoundBound(attr='operate', root=_Operation, parent=self.setup)
        # ---------Balances-------------
        # ----------------------------------------

        # Process
        self.conversion = Balance(
            attr='conversion',
            opn=Process,
            balance=Conversion,
            prmsym='η',
            parent=self.operate,
        )
        # Storage
        self.inventory = Balance(
            attr='inventory',
            opn=Storage,
            balance=Inventory,
            prmsym='φ',
            parent=self.operate,
        )
        # Transit
        self.freight = Balance(
            attr='freight',
            opn=Transit,
            balance=Freight,
            prmsym='ψ',
            parent=self.operate,
        )

        # -----------Exact Calculations-----------
        # ----------------------------------------
        # ---------------Spend/Earn----------------
        # ----Buy--------
        self.buy_spend = Calculate(root=Cash, parent=self.buy, friend=self.spend)
        self.buy_earn = Calculate(root=Cash, parent=self.buy, friend=self.earn)
        # ----Sell--------
        self.sell_earn = Calculate(root=Cash, parent=self.sell, friend=self.earn)
        self.sell_spend = Calculate(root=Cash, parent=self.sell, friend=self.spend)
        # ----Lose--------
        self.lose_spend = Calculate(root=Resource, parent=self.lose, friend=self.spend)
        # ----Recover--------
        self.recover_earn = Calculate(
            root=Resource, parent=self.recover, friend=self.earn
        )
        # ----Use--------
        self.use_spend = Calculate(root=_Used, parent=self.use, friend=self.spend)
        self.use_earn = Calculate(root=_Used, parent=self.use, friend=self.earn)
        # ----Dispose--------
        self.dispose_spend = Calculate(
            root=_Used, parent=self.dispose, friend=self.spend
        )
        self.dispose_earn = Calculate(root=_Used, parent=self.dispose, friend=self.earn)
        # ----SetUp--------
        self.setup_spend = Calculate(
            root=_Operation, parent=self.setup, friend=self.spend
        )
        self.setup_earn = Calculate(
            root=_Operation, parent=self.setup, friend=self.earn
        )
        # ----Dismantle--------
        self.dismantle_spend = Calculate(
            root=_Operation, parent=self.dismantle, friend=self.spend
        )
        self.dismantle_earn = Calculate(
            root=_Operation, parent=self.dismantle, friend=self.earn
        )
        # ----Operate--------
        self.operate_spend = Calculate(
            root=_Operation, parent=self.operate, friend=self.spend
        )
        self.operate_earn = Calculate(
            root=_Operation, parent=self.operate, friend=self.earn
        )

        # ---------------Emit/Sequester----------------
        # ----Buy--------
        self.buy_emit = Calculate(root=Emission, parent=self.buy, friend=self.emit)
        self.buy_sequester = Calculate(
            root=Emission, parent=self.buy, friend=self.sequester
        )
        # ----Sell--------
        self.sell_emit = Calculate(root=Emission, parent=self.sell, friend=self.emit)
        self.sell_sequester = Calculate(
            root=Emission, parent=self.sell, friend=self.sequester
        )
        # ----Lose--------
        self.lose_emit = Calculate(root=Resource, parent=self.lose, friend=self.emit)
        self.recover_sequester = Calculate(
            root=Resource, parent=self.recover, friend=self.sequester
        )
        # ----Use--------
        self.use_emit = Calculate(root=Emission, parent=self.use, friend=self.emit)
        self.use_sequester = Calculate(
            root=Emission, parent=self.use, friend=self.sequester
        )
        # ----Dispose--------
        self.dispose_emit = Calculate(
            root=Emission, parent=self.dispose, friend=self.emit
        )
        self.dispose_sequester = Calculate(
            root=Emission, parent=self.dispose, friend=self.sequester
        )
        # ----SetUp--------
        self.setup_emit = Calculate(root=Emission, parent=self.setup, friend=self.emit)
        self.setup_sequester = Calculate(
            root=Emission, parent=self.setup, friend=self.sequester
        )
        # ----Dismantle--------
        self.dismantle_emit = Calculate(
            root=Emission, parent=self.dismantle, friend=self.emit
        )
        self.dismantle_sequester = Calculate(
            root=Emission, parent=self.dismantle, friend=self.sequester
        )
        # ----Setup--------
        self.setup_emit = Calculate(root=Emission, parent=self.setup, friend=self.emit)
        self.setup_sequester = Calculate(
            root=Emission, parent=self.setup, friend=self.sequester
        )
        # ----Operate--------
        self.operate_emit = Calculate(
            root=Emission, parent=self.operate, friend=self.emit
        )
        self.operate_sequester = Calculate(
            root=Emission, parent=self.operate, friend=self.sequester
        )
        # ---------------Use/Dispose----------------
        # ----Setup--------
        self.setup_use = Calculate(root=_Used, parent=self.setup, friend=self.use)
        # ----Dismantle--------
        self.dismantle_dispose = Calculate(
            root=_Used, parent=self.dismantle, friend=self.dispose
        )
        # ---------------Lose/Recover----------------
        # ----Operate--------
        self.operate_lose = Calculate(
            root=Resource, parent=self.operate, friend=self.lose
        )
        self.operate_recover = Calculate(
            root=Resource, parent=self.operate, friend=self.recover
        )
        # ---------------Lag----------------
        # ----SetUp--------
        self.setup_time = Lag(root=Horizon, parent=self.setup)
        # ----Dismantle--------
        self.dismantle_time = Lag(root=Horizon, parent=self.dismantle)
        # ----Operate--------
        self.operate_time = Lag(root=Horizon, parent=self.operate)

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
    def report_emits(self):
        """Collection of Emissions"""
        return Report(
            name='emits',
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

    def birth_attrs(self, task: str):
        """Returns all Attributes need to birth Variables"""
        return getattr(self, task).birth_attrs()

    def inputs(self):
        """Returns all Inputs"""
        return self.bounds() + self.exacts() + self.boundbounds()
