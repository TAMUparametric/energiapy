""" Loss during operation 
"""

from dataclasses import dataclass

from sympy import IndexedBase

from ..components.commodity.resource import Resource
from ..components.operational.storage import Storage
from ..components.operational.transit import Transit
from ..indices.structure import make_structures
from ._variable import _ExactVar
from .operate import Operate


@dataclass
class Loss(_ExactVar):
    """Loss is the cost of a Component"""

    def __post_init__(self):
        _ExactVar.__post_init__(self)

    @classmethod
    def parent(cls):
        """The Parent Task of the Variable"""
        return Operate

    @classmethod
    def child(cls):
        """The Parent Variable doesnot carry Child Component"""
        return Resource

    @classmethod
    def structures(cls, component):
        """The allowed structures of disposition of the Variable"""

        if isinstance(component, Storage):
            opn, spt = 'stg', 'loc'
        elif isinstance(component, Transit):
            opn, spt = 'trn', 'lnk'

        return make_structures(cmd='res', opn=[opn], spt=[spt, 'ntw'])

    @staticmethod
    def id() -> IndexedBase:
        """Symbol"""
        return IndexedBase('loss')
