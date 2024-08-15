""" Use Task 
"""

from dataclasses import dataclass

from ..components.commodity.land import Land
from ..components.commodity.material import Material
from ..disposition.structure import make_structures
from ._variable import _Variable
from .capacitate import Capacity


@dataclass
class Use(_Variable):
    """Trade changes the ownership of Resource between Players"""

    def __post_init__(self):
        _Variable.__post_init__(self)

    @staticmethod
    def parent():
        """The Parent Task of the Variable"""

    @staticmethod
    def child():
        """The Parent Variable doesnot carry Child Component"""

    @staticmethod
    def structures():
        """The allowed structures of disposition of the Variable"""
        return make_structures(
            cmd=['mat', 'lnd'],
            opn=['pro', 'stg', 'trn'],
            spt=['loc', 'lnk', 'ntw'],
        )


@dataclass
class UseCmd(_Variable):
    """Commodity Use"""

    def __post_init__(self):
        _Variable.__post_init__(self)

    @staticmethod
    def parent():
        """The Parent Task of the Variable"""
        return Capacity

    @staticmethod
    def child():
        """The Parent Variable doesnot carry Child Component"""
        return (Land, Material)


@dataclass
class UseMat(UseCmd):
    """Material Use"""

    def __post_init__(self):
        UseCmd.__post_init__(self)

    @staticmethod
    def structures():
        """The allowed structures of disposition of the Variable"""
        return make_structures(
            cmd='mat',
            opn=['pro', 'stg', 'trn'],
            spt=['loc', 'lnk', 'ntw'],
        )


@dataclass
class UseLnd(UseCmd):
    """Land Use"""

    def __post_init__(self):
        UseCmd.__post_init__(self)

    @staticmethod
    def structures():
        """The allowed structures of disposition of the Variable"""
        return make_structures(
            cmd='lnd',
            opn=['pro', 'stg', 'trn'],
            spt=['loc', 'lnk', 'ntw'],
        )
