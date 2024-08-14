"""Capacity Operations
"""

from dataclasses import dataclass

from ..disposition._structure import make_structures
from ._variable import _Variable


@dataclass
class Capacity(_Variable):
    """Trade changes the ownership of Resource between Players"""

    def __post_init__(self):
        _Variable.__post_init__(self)

    @staticmethod
    def parent():
        """The Parent Task of the task"""
        return None

    @staticmethod
    def structures():
        """The allowed structures of disposition of the task"""
        return make_structures(opn=['pro', 'stg', 'trn'], spt=['loc', 'lnk', 'ntw'])
