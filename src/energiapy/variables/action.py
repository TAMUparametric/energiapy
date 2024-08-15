"""Variables for Actions taken by Players
"""

from dataclasses import dataclass

from ..disposition.structure import make_structures
from ._variable import _Variable


@dataclass
class Action(_Variable):
    """Action is a Player's action"""

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


@dataclass
class Takes(Action):
    """Takes is when Player takes from what they Has(ve)"""

    def __post_init__(self):
        Action.__post_init__(self)