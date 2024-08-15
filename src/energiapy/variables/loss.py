""" Loss during operation 
"""

from dataclasses import dataclass

from ..components.commodity.resource import Resource
from ..disposition.structure import make_structures
from ._variable import _Variable
from .operate import Operate


@dataclass
class Loss(_Variable):
    """Loss is the cost of a Component"""

    def __post_init__(self):
        _Variable.__post_init__(self)

    @staticmethod
    def parent():
        """The Parent Task of the Variable"""
        return Operate

    @staticmethod
    def child():
        """The Parent Variable doesnot carry Child Component"""
        return Resource

    @staticmethod
    def structures():
        """The allowed structures of disposition of the Variable"""
        return make_structures(cmd='res', opn=['stg', 'trn'], spt=['loc', 'lnk', 'ntw'])
