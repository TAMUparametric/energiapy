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


@dataclass
class BndExpense(_Variable):
    """Expense is the cost of a Component"""

    def __post_init__(self):
        _Variable.__post_init__(self)

    @staticmethod
    def structures():
        """The allowed structures of disposition of the Variable"""
        return make_structures(csh_strict=True, spt=['loc', 'lnk', 'ntw'])

    @staticmethod
    def parent():
        """The Parent Task of the Variable"""

    @staticmethod
    def child():
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

    @staticmethod
    def child():
        """The Parent Variable doesnot carry Child Component"""
        return Cash


@dataclass
class ExpTrade(Expense):
    """Resource Expense"""

    def __post_init__(self):
        Expense.__post_init__(self)

    @staticmethod
    def structures():
        """The allowed structures of disposition of the Variable"""
        return make_structures(
            csh_strict=True, cmd='res', opn='pro', spt=['loc', 'ntw']
        )


@dataclass
class ExpBuy(ExpTrade):
    """Buy Expense"""

    def __post_init__(self):
        ExpTrade.__post_init__(self)

    @staticmethod
    def parent():
        """The Parent Task of the Variable"""
        return Buy


@dataclass
class ExpSell(ExpTrade):
    """Sell Expense"""

    def __post_init__(self):
        ExpTrade.__post_init__(self)

    @staticmethod
    def parent():
        """The Parent Task of the Variable"""
        return Sell


@dataclass
class Penalty(ExpTrade):
    """Buy Expense"""

    def __post_init__(self):
        ExpTrade.__post_init__(self)

    @staticmethod
    def parent():
        """The Parent Task of the Variable"""
        return Sell


@dataclass
class Credit(ExpTrade):
    """Credit Earned"""

    def __post_init__(self):
        ExpTrade.__post_init__(self)

    @staticmethod
    def parent():
        """The Parent Task of the Variable"""
        return Operate


@dataclass
class ExpUse(Expense):
    """Use Expense"""

    def __post_init__(self):
        Expense.__post_init__(self)

    @staticmethod
    def parent():
        """The Parent Task of the Variable"""
        return Use

    @staticmethod
    def structures():
        """The allowed structures of disposition of the Variable"""
        return make_structures(
            csh_strict=True,
            cmd=['mat', 'lnd'],
            opn=['pro', 'stg', 'trn'],
            spt=['loc', 'lnk', 'ntw'],
        )


@dataclass
class ExpCap(Expense):
    """Capacity Expense"""

    def __post_init__(self):
        Expense.__post_init__(self)

    @staticmethod
    def parent():
        """The Parent Task of the Variable"""
        return Capacity

    @staticmethod
    def structures():
        """The allowed structures of disposition of the Variable"""
        return make_structures(
            csh_strict=True, opn=['pro', 'stg', 'trn'], spt=['loc', 'lnk', 'ntw']
        )


@dataclass
class ExpOp(Expense):
    """Operate Expense"""

    def __post_init__(self):
        Expense.__post_init__(self)

    @staticmethod
    def parent():
        """The Parent Task of the Variable"""
        return Operate

    @staticmethod
    def structures():
        """The allowed structures of disposition of the Variable"""
        return make_structures(
            csh_strict=True, opn=['pro', 'stg', 'trn'], spt=['loc', 'lnk', 'ntw']
        )
