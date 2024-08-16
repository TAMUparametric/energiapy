"""Emissions from various sources.
"""

from dataclasses import dataclass

from ..components.impact.emission import Emission
from ..disposition.structure import make_structures
from ._variable import _Variable
from .capacitate import Capacity
from .loss import Loss
from .trade import Buy, Sell
from .use import Use


@dataclass
class EmitSys(_Variable):
    """System Emit"""

    def __post_init__(self):
        _Variable.__post_init__(self)

    @staticmethod
    def structures():
        """The allowed structures of disposition of the Variable"""
        return make_structures(emn_strict=True, spt=['loc', 'lnk', 'ntw'])

    @staticmethod
    def parent():
        """The Parent Task of the Variable"""

    @staticmethod
    def child():
        """The Parent Variable doesnot carry Child Component"""


@dataclass
class Emit(_Variable):
    """Emit changes the ownership of Resource between Players"""

    def __post_init__(self):
        _Variable.__post_init__(self)

    @staticmethod
    def child():
        """The Parent Variable doesnot carry Child Component"""
        return Emission


@dataclass
class EmitTrade(Emit):
    """Resource Emit"""

    def __post_init__(self):
        Emit.__post_init__(self)

    @staticmethod
    def structures():
        """The allowed structures of disposition of the Variable"""
        return make_structures(
            emn_strict=True, cmd='res', opn='pro', spt=['loc', 'ntw']
        )


@dataclass
class EmitBuy(EmitTrade):
    """Buy Emit"""

    def __post_init__(self):
        EmitTrade.__post_init__(self)

    @staticmethod
    def parent():
        """The Parent Task of the Variable"""
        return Buy


@dataclass
class EmitSell(EmitTrade):
    """Sell Emit"""

    def __post_init__(self):
        EmitTrade.__post_init__(self)

    @staticmethod
    def parent():
        """The Parent Task of the Variable"""
        return Sell


@dataclass
class EmitLoss(Emit):
    """Loss Emit"""

    def __post_init__(self):
        Emit.__post_init__(self)

    @staticmethod
    def parent():
        """The Parent Task of the Variable"""
        return Loss

    @staticmethod
    def structures():
        """The allowed structures of disposition of the Variable"""
        return make_structures(
            emn_strict=True, cmd='res', opn=['stg', 'trn'], spt=['loc', 'lnk', 'ntw']
        )


@dataclass
class EmitUse(Emit):
    """Use Emit"""

    def __post_init__(self):
        Emit.__post_init__(self)

    @staticmethod
    def parent():
        """The Parent Task of the Variable"""
        return Use

    @staticmethod
    def structures():
        """The allowed structures of disposition of the Variable"""
        return make_structures(
            mde=True,
            emn_strict=True,
            cmd=['mat', 'lnd'],
            opn=['pro', 'stg', 'trn'],
            spt=['loc', 'lnk', 'ntw'],
        )


@dataclass
class EmitCap(Emit):
    """Operation Capacity related Emit"""

    def __post_init__(self):
        Emit.__post_init__(self)

    @staticmethod
    def parent():
        """The Parent Task of the Variable"""
        return Capacity

    @staticmethod
    def structures():
        """The allowed structures of disposition of the Variable"""
        return make_structures(
            mde=True,
            emn_strict=True,
            opn=['pro', 'stg', 'trn'],
            spt=['loc', 'lnk', 'ntw'],
        )
