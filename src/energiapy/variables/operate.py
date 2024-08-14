"""Operate Operations
"""

from dataclasses import dataclass

from ..disposition.structure import make_structures
from ._variable import _Variable
from .capacitate import Capacity


@dataclass
class Operate(_Variable):
    """Trade changes the ownership of Resource between Players"""

    def __post_init__(self):
        _Variable.__post_init__(self)

    @staticmethod
    def parent():
        """The Parent Task of the task"""
        return Capacity

    @staticmethod
    def structures():
        """The allowed structures of disposition of the task"""
        return make_structures(opn=['pro', 'stg', 'trn'], spt=['loc', 'lnk', 'ntw'])
