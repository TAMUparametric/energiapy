""" Use Task 
"""

from dataclasses import dataclass

from sympy import IndexedBase

from ..components.commodity.land import Land
from ..components.commodity.material import Material
from ..components.operational.process import Process
from ..components.operational.storage import Storage
from ..components.operational.transit import Transit
from ..dispositions.structure import make_structures
from ._variable import _BoundVar, _ExactVar
from .capacitate import Capacity


@dataclass
class Use(_BoundVar):
    """Trade changes the ownership of Useable Commodity between Players"""

    def __post_init__(self):
        _BoundVar.__post_init__(self)

    @classmethod
    def parent(cls):
        """The Parent Task of the Variable"""

    @classmethod
    def child(cls):
        """The Parent Variable doesnot carry Child Component"""

    @classmethod
    def structures(cls, component):
        """The allowed structures of disposition of the Variable"""

        if isinstance(component, Land):
            cmd = 'lnd'
        elif isinstance(component, Material):
            cmd = 'mat'
        return make_structures(
            cmd=[cmd],
            opn=['pro', 'stg', 'trn'],
            spt=['loc', 'lnk', 'ntw'],
        )

    @staticmethod
    def id() -> IndexedBase:
        """Symbol"""
        return IndexedBase('use')


@dataclass
class UseSetUp(_ExactVar):
    """Commodity Use"""

    def __post_init__(self):
        _ExactVar.__post_init__(self)

    @classmethod
    def parent(cls):
        """The Parent Task of the Variable"""
        return Capacity

    @classmethod
    def structures(cls, component):
        """The allowed structures of disposition of the Variable"""

        if isinstance(component, Process):
            opn, spt = 'pro', 'loc'
        elif isinstance(component, Storage):
            opn, spt = 'stg', 'loc'
        elif isinstance(component, Transit):
            opn, spt = 'trn', 'lnk'
        return make_structures(
            cmd=['lnd', 'mat'],
            mde=True,
            opn=[opn],
            spt=[spt, 'ntw'],
        )

    @classmethod
    def child(cls):
        """The Parent Variable doesnot carry Child Component"""
        return (Land, Material)

    @staticmethod
    def id() -> IndexedBase:
        """Symbol"""
        return IndexedBase('use^setup')
