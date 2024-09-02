""" Loss during operation 
"""

from dataclasses import dataclass

from sympy import IndexedBase

from ....components.commodity.resource import Resource
from ....components.operation.storage import Storage
from ....components.operation.transit import Transit
from ...disposition.structure import make_structures
from .._variable import _ExactVar
from ..boundbounds.operate import Operate


@dataclass
class Lose(_ExactVar):
    """Lose is when a Resource is lost during operation"""

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
