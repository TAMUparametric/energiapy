""" Loss during operation 
"""

from dataclasses import dataclass

from .._core._layout._structure import make_structures
from ._variable import _Variable
from .operate import Operate


@dataclass
class Loss(_Variable):
    """Loss is the cost of a Component"""

    def __post_init__(self):
        _Variable.__post_init__(self)

    @staticmethod
    def _parent():
        """The Parent Task of the task"""
        return Operate

    @staticmethod
    def _structures():
        """The allowed structures of disposition of the task"""
        return make_structures(cmd='res', opn=['stg', 'trn'], spt=['loc', 'lnk', 'ntw'])
