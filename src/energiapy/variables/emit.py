"""Emissions from various sources.
"""

from dataclasses import dataclass

from ..disposition._structure import make_structures
from ._variable import _Variable
from .capacitate import Capacity
from .loss import Loss
from .trade import Buy, Sell
from .use import Use


@dataclass
class Emit(_Variable):
    """Emit changes the ownership of Resource between Players"""

    def __post_init__(self):
        _Variable.__post_init__(self)

    @staticmethod
    def parent():
        """The Parent Task of the task"""
        return None


@dataclass
class EmitSys(Emit):
    """System Emit"""

    def __post_init__(self):
        Emit.__post_init__(self)

    @staticmethod
    def structures():
        """The allowed structures of disposition of the task"""
        return make_structures(emn=True, spt=['loc', 'lnk', 'ntw'])

    @staticmethod
    def parent():
        """The Parent Task of the task"""
        return None


@dataclass
class EmitTrade(Emit):
    """Resource Emit"""

    def __post_init__(self):
        Emit.__post_init__(self)

    @staticmethod
    def structures():
        """The allowed structures of disposition of the task"""
        return make_structures(emn=True, cmd='res', opn='pro', spt=['loc', 'ntw'])


@dataclass
class EmitBuy(EmitTrade):
    """Buy Emit"""

    def __post_init__(self):
        EmitTrade.__post_init__(self)

    @staticmethod
    def parent():
        """The Parent Task of the task"""
        return Buy


@dataclass
class EmitSell(EmitTrade):
    """Sell Emit"""

    def __post_init__(self):
        EmitTrade.__post_init__(self)

    @staticmethod
    def parent():
        """The Parent Task of the task"""
        return Sell


@dataclass
class EmitLoss(Emit):
    """Loss Emit"""

    def __post_init__(self):
        Emit.__post_init__(self)

    @staticmethod
    def parent():
        """The Parent Task of the task"""
        return Loss

    @staticmethod
    def structures():
        """The allowed structures of disposition of the task"""
        return make_structures(
            emn=True, cmd='res', opn=['stg', 'trn'], spt=['loc', 'lnk', 'ntw']
        )


@dataclass
class EmitUse(Emit):
    """Use Emit"""

    def __post_init__(self):
        Emit.__post_init__(self)

    @staticmethod
    def parent():
        """The Parent Task of the task"""
        return Use

    @staticmethod
    def structures():
        """The allowed structures of disposition of the task"""
        return make_structures(
            emn=True,
            cmd=['mat', 'lnd'],
            opn=['pro', 'stg', 'trn'],
            spt=['loc', 'lnk', 'ntw'],
        )


@dataclass
class EmitOpn(Emit):
    """Operation Capacity related Emit"""

    def __post_init__(self):
        Emit.__post_init__(self)

    @staticmethod
    def parent():
        """The Parent Task of the task"""
        return Capacity

    @staticmethod
    def structures():
        """The allowed structures of disposition of the task"""
        return make_structures(
            emn=True, opn=['pro', 'stg', 'trn'], spt=['loc', 'lnk', 'ntw']
        )
