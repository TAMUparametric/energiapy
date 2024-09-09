"""Task Master relates attributes to Elements
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import TYPE_CHECKING


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
from ...components.temporal.horizon import Horizon

from ...elements.parameters.balances.conversion import Conversion
from ...elements.parameters.balances.freight import Freight
from ...elements.parameters.balances.inventory import Inventory

if TYPE_CHECKING:
    from ...elements.constraints.rules._rule import _Rule
    from ...elements.constraints._constraint import _Constraint


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
        self.spend = Bound(attr='spend', root=Cash)
        self.earn = Bound(attr='earn', root=Cash, sibling=self.spend)
        # Emission
        self.emit = Bound(attr='emit', root=Emission)
        self.sequester = Bound(attr='sequester', root=Emission, sibling=self.emit)
        # Resource | Land
        self.use = Bound(attr='use', root=Resource)
        self.dispose = Bound(attr='dispose', root=Resource, sibling=self.use)
        # Resource
        self.buy = Bound(attr='buy', root=Resource)
        self.sell = Bound(attr='sell', root=Resource, sibling=self.buy)
        self.receive = Bound(attr='receive', root=Resource)
        self.ship = Bound(attr='ship', root=Resource, sibling=self.receive)
        self.recover = Bound(attr='recover', root=Resource)
        self.lose = Bound(attr='lose', root=Resource, sibling=self.recover)

        # Operational
        self.setup = Bound(attr='setup', root=_Operation)
        self.dismantle = Bound(attr='dismantle', root=_Operation, sibling=self.setup)

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
            sym='η',
            parent=self.operate,
        )
        # Storage
        self.inventory = Balance(
            attr='inventory',
            opn=Storage,
            balance=Inventory,
            sym='φ',
            parent=self.operate,
        )
        # Transit
        self.freight = Balance(
            attr='freight',
            opn=Transit,
            balance=Freight,
            sym='ψ',
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
        self.use_spend = Calculate(root=Resource, parent=self.use, friend=self.spend)
        self.use_earn = Calculate(root=Resource, parent=self.use, friend=self.earn)
        # ----Dispose--------
        self.dispose_spend = Calculate(
            root=Resource, parent=self.dispose, friend=self.spend
        )
        self.dispose_earn = Calculate(
            root=Resource, parent=self.dispose, friend=self.earn
        )
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
        self.setup_use = Calculate(root=Resource, parent=self.setup, friend=self.use)
        # ----Dismantle--------
        self.dismantle_dispose = Calculate(
            root=Resource, parent=self.dismantle, friend=self.dispose
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
    def report_transact(self):
        """Collection of Transacts"""
        return Report(
            name='transactions',
            tasks=[getattr(self, attr) for attr in self.transacts()],
        )

    @property
    def report_use(self):
        """Collection of Uses"""
        return Report(
            name='uses',
            tasks=[getattr(self, attr) for attr in self.uses()],
        )

    @property
    def report_emit(self):
        """Collection of Emissions"""
        return Report(
            name='emits',
            tasks=[getattr(self, attr) for attr in self.emits()],
        )

    @property
    def report_lose(self):
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

    def inputs(self):
        """Returns all Inputs"""
        return self.bounds() + self.exacts() + self.boundbounds()

    def cns(self, attr: str) -> _Constraint:
        """Returns the Constraint associated with the attribute"""
        return getattr(self, attr)

    def var(self, attr: str):
        """Returns the Variable"""
        return self.cns(attr).var()

    def prm(self, attr: str):
        """Returns the Parameter"""
        return self.cns(attr).prm()

    def rule(self, attr: str):
        """Returns the Constraint"""
        return self.cns(attr).rule()

    def varsym(self, attr: str):
        """Returns the Variable Symbol"""
        return self.cns(attr).varsym

    def prmsym(self, attr: str):
        """Returns the Parameter Symbol"""
        return self.cns(attr).prmsym

    def varbirth_attrs(self, attr: str):
        """Returns the Variable Attributes"""
        return self.cns(attr).varbirth_attrs()
