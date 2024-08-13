from dataclasses import dataclass

from .._core._layout._structure import make_structures
from ._variable import _Variable
from .capacitate import Capacitate
from .operate import Operate
from .trade import Buy, Sell
from .use import Use


@dataclass
class Expense(_Variable):
    """Expense is the cost of a Component"""

    def __post_init__(self):
        _Variable.__post_init__(self)


@dataclass
class ExpSys(Expense):
    """System Expense"""

    def __post_init__(self):
        Expense.__post_init__(self)

    @staticmethod
    def _structures():
        """The allowed structures of disposition of the task"""
        return make_structures(csh=True, spt=['loc', 'lnk', 'ntw'])

    @staticmethod
    def _parent():
        """The Parent Task of the task"""
        return None


@dataclass
class ExpTrade(Expense):
    """Resource Expense"""

    def __post_init__(self):
        Expense.__post_init__(self)

    @staticmethod
    def _structures():
        """The allowed structures of disposition of the task"""
        return make_structures(csh=True, cmd='res', opn='pro', spt=['loc', 'ntw'])


@dataclass
class ExpBuy(ExpTrade):
    """Buy Expense"""

    def __post_init__(self):
        ExpTrade.__post_init__(self)

    @staticmethod
    def _parent():
        """The Parent Task of the task"""
        return Buy


@dataclass
class ExpSell(ExpTrade):
    """Sell Expense"""

    def __post_init__(self):
        ExpTrade.__post_init__(self)

    @staticmethod
    def _parent():
        """The Parent Task of the task"""
        return Sell


@dataclass
class Penalty(ExpTrade):
    """Buy Expense"""

    def __post_init__(self):
        ExpTrade.__post_init__(self)

    @staticmethod
    def _parent():
        """The Parent Task of the task"""
        return Sell


@dataclass
class Credit(ExpTrade):
    """Credit Earned"""

    def __post_init__(self):
        ExpTrade.__post_init__(self)

    @staticmethod
    def _parent():
        """The Parent Task of the task"""
        return Operate


@dataclass
class ExpUse(Expense):
    """Use Expense"""

    def __post_init__(self):
        Expense.__post_init__(self)

    @staticmethod
    def _parent():
        """The Parent Task of the task"""
        return Use

    @staticmethod
    def _structures():
        """The allowed structures of disposition of the task"""
        return make_structures(
            csh=True,
            cmd=['mat', 'lnd'],
            opn=['pro', 'stg', 'trn'],
            spt=['loc', 'lnk', 'ntw'],
        )


@dataclass
class ExpCap(Expense):
    """Capacitate Expense"""

    def __post_init__(self):
        Expense.__post_init__(self)

    @staticmethod
    def _parent():
        """The Parent Task of the task"""
        return Capacitate

    @staticmethod
    def _structures():
        """The allowed structures of disposition of the task"""
        return make_structures(
            csh=True, opn=['pro', 'stg', 'trn'], spt=['loc', 'lnk', 'ntw']
        )


@dataclass
class ExpOp(Expense):
    """Operate Expense"""

    def __post_init__(self):
        Expense.__post_init__(self)

    @staticmethod
    def _parent():
        """The Parent Task of the task"""
        return Operate

    @staticmethod
    def _structures():
        """The allowed structures of disposition of the task"""
        return make_structures(
            csh=True, opn=['pro', 'stg', 'trn'], spt=['loc', 'lnk', 'ntw']
        )


  