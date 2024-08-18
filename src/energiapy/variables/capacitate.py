"""Capacity Operations
"""

from dataclasses import dataclass

from ..disposition.structure import make_structures
from ._variable import _Variable
from ..components.operational.process import Process
from ..components.operational.storage import Storage
from ..components.operational.transit import Transit


@dataclass
class Capacity(_Variable):
    """Trade changes the ownership of Resource between Players"""

    def __post_init__(self):
        _Variable.__post_init__(self)

    @classmethod
    def parent(cls):
        """The Parent Task of the Variable"""

    @classmethod
    def child(cls):
        """The Parent Variable doesnot carry Child Component"""

    @classmethod
    def structures(cls, component):
        """The allowed structures of disposition of the Variable"""
        if isinstance(component, Process):
            opn, spt = 'pro', 'loc'
        elif isinstance(component, Storage):
            opn, spt = 'stg', 'loc'
        elif isinstance(component, Transit):
            opn, spt = 'trn', 'lnk'

        return make_structures(mde=True, opn=[opn], spt=[spt, 'ntw'])
