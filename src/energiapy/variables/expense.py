"""Variables for Expense
"""

from dataclasses import dataclass

from ..components.commodity.cash import Cash
from ..disposition.structure import make_structures
from ._variable import _Variable
from .capacitate import Capacity
from .operate import Operate
from .trade import Buy, Sell
from .use import Use
from ..components.commodity.material import Material
from ..components.commodity.land import Land
from ..components.operational.process import Process
from ..components.operational.storage import Storage
from ..components.operational.transit import Transit


@dataclass
class BndExpense(_Variable):
    """Expense is the cost of a Component"""

    def __post_init__(self):
        _Variable.__post_init__(self)

    @classmethod
    def structures(cls, component):
        """The allowed structures of disposition of the Variable"""
        return make_structures(csh_strict=True, spt=['loc', 'lnk', 'ntw'])

    @classmethod
    def parent(cls):
        """The Parent Task of the Variable"""

    @classmethod
    def child(cls):
        """The Parent Variable doesnot carry Child Component"""


@dataclass
class Spend(BndExpense):
    """System Expense"""

    def __post_init__(self):
        BndExpense.__post_init__(self)


@dataclass
class Earn(BndExpense):
    """System Expense"""

    def __post_init__(self):
        BndExpense.__post_init__(self)


@dataclass
class Expense(_Variable):
    """Expense is the cost of a Component"""

    def __post_init__(self):
        _Variable.__post_init__(self)

    @classmethod
    def child(cls):
        """The Parent Variable doesnot carry Child Component"""
        return Cash


@dataclass
class ExpTrade(Expense):
    """Resource Expense"""

    def __post_init__(self):
        Expense.__post_init__(self)

    @classmethod
    def structures(cls, component):
        """The allowed structures of disposition of the Variable"""
        return make_structures(
            csh_strict=True, cmd='res', opn='pro', spt=['loc', 'ntw']
        )


@dataclass
class ExpBuy(ExpTrade):
    """Buy Expense"""

    def __post_init__(self):
        ExpTrade.__post_init__(self)

    @classmethod
    def parent(cls):
        """The Parent Task of the Variable"""
        return Buy


@dataclass
class ExpSell(ExpTrade):
    """Sell Expense"""

    def __post_init__(self):
        ExpTrade.__post_init__(self)

    @classmethod
    def parent(cls):
        """The Parent Task of the Variable"""
        return Sell


@dataclass
class Penalty(ExpTrade):
    """Buy Expense"""

    def __post_init__(self):
        ExpTrade.__post_init__(self)

    @classmethod
    def parent(cls):
        """The Parent Task of the Variable"""
        return Sell


@dataclass
class Credit(ExpTrade):
    """Credit Earned"""

    def __post_init__(self):
        ExpTrade.__post_init__(self)

    @classmethod
    def parent(cls):
        """The Parent Task of the Variable"""
        return Sell


@dataclass
class ExpUse(Expense):
    """Use Expense"""

    def __post_init__(self):
        Expense.__post_init__(self)

    @classmethod
    def parent(cls):
        """The Parent Task of the Variable"""
        return Use

    @classmethod
    def structures(cls, component):
        """The allowed structures of disposition of the Variable"""

        if isinstance(component, Land):
            cmd = 'lnd'
        elif isinstance(component, Material):
            cmd = 'mat'
        return make_structures(
            mde=True,
            csh_strict=True,
            cmd=[cmd],
            opn=['pro', 'stg', 'trn'],
            spt=['loc', 'lnk', 'ntw'],
        )


@dataclass
class ExpOpn(Expense):
    """Capacity Expense"""

    def __post_init__(self):
        Expense.__post_init__(self)

    @classmethod
    def structures(cls, component):
        """The allowed structures of disposition of the Variable"""

        if isinstance(component, Process):
            opn, spt = 'pro', 'loc'
        elif isinstance(component, Storage):
            opn, spt = 'stg', 'loc'
        elif isinstance(component, Transit):
            opn, spt = 'trn', 'lnk'

        return make_structures(
            csh_strict=True,
            mde=True,
            opn=[opn],
            spt=[spt, 'ntw'],
        )


@dataclass
class ExpCap(ExpOpn):
    """Capacity Expense"""

    def __post_init__(self):
        ExpOpn.__post_init__(self)

    @classmethod
    def parent(cls):
        """The Parent Task of the Variable"""
        return Capacity


@dataclass
class ExpOp(ExpOpn):
    """Operate Expense"""

    def __post_init__(self):
        ExpOpn.__post_init__(self)

    @classmethod
    def parent(cls):
        """The Parent Task of the Variable"""
        return Operate


@dataclass
class ExpOpnI(ExpOpn):
    """Incidental Expense for Operation"""

    def __post_init__(self):
        ExpOpn.__post_init__(self)

    @classmethod
    def parent(cls):
        """The Parent Task of the Variable"""


@dataclass
class ExpCapI(ExpOpnI):
    """Incidental Capital Expense"""

    def __post_init__(self):
        ExpOpnI.__post_init__(self)


@dataclass
class ExpOpI(ExpOpnI):
    """Incidental Operational Expense"""

    def __post_init__(self):
        ExpOpnI.__post_init__(self)
