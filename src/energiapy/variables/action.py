"""Variables for Actions taken by Players
"""

from dataclasses import dataclass

from sympy import IndexedBase

from ..indices.structure import make_structures
from ._variable import _BoundVar


@dataclass
class Action(_BoundVar):
    """Action is a Player's action
    This is a parent class
    """

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
class Give(Action):
    """Give is when a player gives from what they Need(s)"""

    def __post_init__(self):
        Action.__post_init__(self)

    @staticmethod
    def id() -> IndexedBase:
        """ID to add to name"""
        return IndexedBase('gives')


@dataclass
class Take(Action):
    """Take is when Player takes from what they Has(ve)"""

    def __post_init__(self):
        Action.__post_init__(self)

    @staticmethod
    def id() -> IndexedBase:
        """ID to add to name"""
        return IndexedBase('takes')
