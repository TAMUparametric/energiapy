"""Task Master relates attributes to Elements
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import TYPE_CHECKING, Any

from ...components._attrs._balances import _BalanceAttrs
from ...components._attrs._boundbounds import _BoundBoundAttrs
from ...components._attrs._bounds import _BoundAttrs
from ...components._attrs._exacts import _ExactAttrs
# from ...components.analytical.player import Player
from ...components.commodity.cash import Cash
from ...components.commodity.emission import Emission
from ...components.commodity.resource import Resource
from ...components.operation._operation import _Operation
from ...components.operation.process import Process
from ...components.operation.storage import Storage
from ...components.operation.transit import Transit
from ...components.temporal.horizon import Horizon
from ...core._handy._dunders import _Dunders
from ...elements.constraints.balance import Balance
from ...elements.constraints.bound import Bound
from ...elements.constraints.boundbound import BoundBound
from ...elements.constraints.calculate import Calculate
from ...elements.constraints.lag import Lag
from ...elements.constraints.report import Report
from ...elements.parameters.balances.conversion import Conversion
from ...elements.parameters.balances.freight import Freight
from ...elements.parameters.balances.inventory import Inventory

if TYPE_CHECKING:
    from ...elements.constraints._constraint import _Constraint
    from ...elements.constraints.rules._rule import _Rule


@dataclass
class Chanakya(_BoundAttrs, _BoundBoundAttrs, _ExactAttrs, _BalanceAttrs, _Dunders):
    """This object collects all the attributes defined
    and makes a list of Indexs they are defined at

    """

    name: str = field(default=None)

    def __post_init__(self):
        self.name = f'TaskMaster|{self.name}|'
        # ---------Bounds-------------------------
        self.spend = Bound(root=Cash)
        self.earn = Bound(sibling=self.spend)
        # Emission
        self.emit = Bound(root=Emission)
        self.sequester = Bound(sibling=self.emit)
        # Resource | Land
        self.use = Bound(root=Resource)
        self.dispose = Bound(sibling=self.use)
        # Resource
        self.buy = Bound(root=Resource)
        self.sell = Bound(sibling=self.buy)
        self.receive = Bound(root=Resource)
        self.ship = Bound(sibling=self.receive)
        self.recover = Bound(root=Resource)
        self.lose = Bound(sibling=self.recover)
        # Operational
        self.setup = Bound(root=_Operation)
        self.dismantle = Bound(sibling=self.setup)

        # ----------BoundBounds-----------
        self.operate = BoundBound(parent=self.setup)
        # ---------Balances-------------
        # Process
        self.conversion = Balance(
            opn=Process,
            balance=Conversion,
            sym='η',
            parent=self.operate,
        )
        # Storage
        self.inventory = Balance(
            opn=Storage,
            balance=Inventory,
            sym='φ',
            parent=self.operate,
        )
        # Transit
        self.freight = Balance(
            opn=Transit,
            balance=Freight,
            sym='ψ',
            parent=self.operate,
        )

        # -----------Exact Calculations-----------
        # ---------------Spend/Earn----------------
        # Buy/Sell
        self.buy_spend = Calculate(parent=self.buy, ilk=self.spend)
        self.buy_earn = Calculate(parent=self.buy, ilk=self.earn)
        self.sell_spend = Calculate(parent=self.sell, ilk=self.spend)
        self.sell_earn = Calculate(parent=self.sell, ilk=self.earn)
        # Use/Dispose
        self.use_spend = Calculate(parent=self.use, ilk=self.spend)
        self.use_earn = Calculate(parent=self.use, ilk=self.earn)
        self.dispose_spend = Calculate(parent=self.dispose, ilk=self.spend)
        self.dispose_earn = Calculate(parent=self.dispose, ilk=self.earn)
        # Setup/Dismantle
        self.setup_spend = Calculate(parent=self.setup, ilk=self.spend)
        self.setup_earn = Calculate(parent=self.setup, ilk=self.earn)
        self.dismantle_spend = Calculate(parent=self.dismantle, ilk=self.spend)
        self.dismantle_earn = Calculate(parent=self.dismantle, ilk=self.earn)
        # Operate
        self.operate_spend = Calculate(parent=self.operate, ilk=self.spend)
        self.operate_earn = Calculate(parent=self.operate, ilk=self.earn)

        # ---------------Emit/Sequester----------------
        # Buy/Sell
        self.buy_emit = Calculate(parent=self.buy, ilk=self.emit)
        self.buy_sequester = Calculate(parent=self.buy, ilk=self.sequester)
        self.sell_emit = Calculate(parent=self.sell, ilk=self.emit)
        self.sell_sequester = Calculate(parent=self.sell, ilk=self.sequester)
        # Lose
        self.lose_emit = Calculate(parent=self.lose, ilk=self.emit)
        self.recover_sequester = Calculate(parent=self.recover, ilk=self.sequester)
        # Use/Dispose
        self.use_emit = Calculate(parent=self.use, ilk=self.emit)
        self.use_sequester = Calculate(parent=self.use, ilk=self.sequester)
        self.dispose_emit = Calculate(parent=self.dispose, ilk=self.emit)
        self.dispose_sequester = Calculate(parent=self.dispose, ilk=self.sequester)
        # Setup/Dismantle
        self.setup_emit = Calculate(parent=self.setup, ilk=self.emit)
        self.setup_sequester = Calculate(parent=self.setup, ilk=self.sequester)
        self.dismantle_emit = Calculate(parent=self.dismantle, ilk=self.emit)
        self.dismantle_sequester = Calculate(parent=self.dismantle, ilk=self.sequester)
        # Operate
        self.operate_emit = Calculate(parent=self.operate, ilk=self.emit)
        self.operate_sequester = Calculate(parent=self.operate, ilk=self.sequester)
        # ---------------Use/Dispose----------------
        # Setup
        self.setup_use = Calculate(parent=self.setup, ilk=self.use)
        # Dismantle
        self.dismantle_dispose = Calculate(parent=self.dismantle, ilk=self.dispose)
        # ---------------Lose/Recover----------------
        # Operate
        self.operate_lose = Calculate(parent=self.operate, ilk=self.lose)
        self.operate_recover = Calculate(parent=self.operate, ilk=self.recover)
        # ---------------Rates----------------
        # SetUp
        self.setup_time = Lag(root=Horizon, parent=self.setup)
        # Dismantle
        self.dismantle_time = Lag(root=Horizon, parent=self.dismantle)
        # Operate
        self.operate_time = Lag(root=Horizon, parent=self.operate)

    def __setattr__(self, name: str, value: _Constraint):

        if not isinstance(value, str):
            value.attr = name

        super().__setattr__(name, value)

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
