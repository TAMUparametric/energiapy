"""Capacitate Operations
"""

from dataclasses import dataclass

from .._core._layout._structure import make_structures
from ._variable import _Variable


@dataclass
class Capacitate(_Variable):
    """Trade changes the ownership of Resource between Players"""

    def __post_init__(self):
        _Variable.__post_init__(self)

    @staticmethod
    def _parent():
        """The Parent Task of the task"""
        return None

    @staticmethod
    def _structures():
        """The allowed structures of disposition of the task"""
        return make_structures(opn=['pro', 'stg', 'trn'], spt=['loc', 'lnk', 'ntw'])
