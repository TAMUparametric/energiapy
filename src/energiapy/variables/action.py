"""Variables for Actions taken by Players
"""

from dataclasses import dataclass

from ..disposition.structure import make_structures
from ._variable import _Variable
from sympy import IndexedBase


@dataclass
class Action(_Variable):
    """Action is a Player's action"""

    @classmethod
    def parent(cls):
        """The Parent Task of the Variable"""

    @classmethod
    def child(cls):
        """The Parent Variable doesnot carry Child Component"""

    @classmethod
    def structures(cls, component):
        """The allowed structures of disposition of the Variable"""
        return make_structures(
            cmd=['csh', 'res', 'mat', 'lnd'],
            opn=['pro', 'stg', 'trn'],
            spt=['loc', 'lnk', 'ntw'],
            ply_strict=True,
            cmd_strict=False,
        )


@dataclass
class Gives(Action):
    """Gives is when a player gives from what they Need(s)"""

    def __post_init__(self):
        Action.__post_init__(self)
    
    @staticmethod
    def id() -> IndexedBase:
        """ID to add to name"""
        return IndexedBase('gives')


@dataclass
class Takes(Action):
    """Takes is when Player takes from what they Has(ve)"""

    def __post_init__(self):
        Action.__post_init__(self)

    @staticmethod
    def id() -> IndexedBase:
        """ID to add to name"""
        return IndexedBase('takes')