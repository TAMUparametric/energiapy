"""Emissions from various sources.
"""

from dataclasses import dataclass

from sympy import IndexedBase

from ...components.commodity.emission import Emission
from ...components.commodity.land import Land
from ...components.commodity.material import Material
from ...components.operation.process import Process
from ...components.operation.storage import Storage
from ...components.operation.transit import Transit
from ..disposition.structure import make_structures
from ._variable import _BoundVar, _ExactVar
from .lose import Lose
from .setup import Capacitate
from .trade import Buy, Sell
from .use import Use

# ---------------MixIns---------------


@dataclass
class _Emit(_ExactVar):
    """Emit is a general variable for how much is Emitted
    This is a parent class
    """

    def __post_init__(self):
        _ExactVar.__post_init__(self)

    @classmethod
    def child(cls):
        """The Parent Variable doesnot carry Child Component"""
        return Emission


@dataclass
class _EmitTrd(_Emit):
    """Resource Emit
    This is a parent class
    """

    def __post_init__(self):
        _Emit.__post_init__(self)

    @classmethod
    def structures(cls, component):
        """The allowed structures of disposition of the Variable"""
        return make_structures(
            emission_strict=True, cmd='res', opn='pro', spt=['loc', 'ntw']
        )


# -------------Variables---------------


@dataclass
class Emit(_BoundVar):
    """Emission emit bound"""

    def __post_init__(self):
        _BoundVar.__post_init__(self)

    @classmethod
    def structures(cls, component):
        """The allowed structures of disposition of the Variable"""
        return make_structures(emission_strict=True, spt=['loc', 'lnk', 'ntw'])

    @classmethod
    def parent(cls):
        """The Parent Task of the Variable"""

    @classmethod
    def child(cls):
        """The Parent Variable doesnot carry Child Component"""

    @staticmethod
    def id() -> IndexedBase:
        """Symbol"""
        return IndexedBase('emit^sys')


@dataclass
class EmitBuy(_EmitTrd):
    """Buy Emit"""

    def __post_init__(self):
        _EmitTrd.__post_init__(self)

    @classmethod
    def parent(cls):
        """The Parent Task of the Variable"""
        return Buy

    @staticmethod
    def id() -> IndexedBase:
        """Symbol"""
        return IndexedBase('emit^buy')


@dataclass
class EmitSll(_EmitTrd):
    """Sell Emit"""

    def __post_init__(self):
        _EmitTrd.__post_init__(self)

    @classmethod
    def parent(cls):
        """The Parent Task of the Variable"""
        return Sell

    @staticmethod
    def id() -> IndexedBase:
        """Symbol"""
        return IndexedBase('emit^sell')


@dataclass
class EmitLse(_Emit):
    """Loss Emit"""

    def __post_init__(self):
        _Emit.__post_init__(self)

    @classmethod
    def parent(cls):
        """The Parent Task of the Variable"""
        return Lose

    @classmethod
    def structures(cls, component):
        """The allowed structures of disposition of the Variable"""
        if isinstance(component, Storage):
            opn, spt = 'stg', 'loc'
        elif isinstance(component, Transit):
            opn, spt = 'trn', 'lnk'

        return make_structures(
            emission_strict=True, cmd='res', opn=[opn], spt=[spt, 'ntw']
        )

    @staticmethod
    def id() -> IndexedBase:
        """Symbol"""
        return IndexedBase('emit^loss')


@dataclass
class EmitUse(_Emit):
    """Use Emit"""

    def __post_init__(self):
        _Emit.__post_init__(self)

    @classmethod
    def parent(cls):
        """The Parent Task of the Variable"""
        return Use

    @classmethod
    def structures(cls, component):
        """The allowed structures of disposition of the Variable"""

        if isinstance(component, Land):
            cmd = 'lnd'
        elif isinstance(component, Material):
            cmd = 'mat'
        return make_structures(
            mde=True,
            emission_strict=True,
            cmd=[cmd],
            opn=['pro', 'stg', 'trn'],
            spt=['loc', 'lnk', 'ntw'],
        )

    @staticmethod
    def id() -> IndexedBase:
        """Symbol"""
        return IndexedBase('emit^use')


@dataclass
class EmitStp(_Emit):
    """Operation Capacitate related Emit"""

    def __post_init__(self):
        _Emit.__post_init__(self)

    @classmethod
    def parent(cls):
        """The Parent Task of the Variable"""
        return Capacitate

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
            mde=True,
            emission_strict=True,
            opn=[opn],
            spt=[spt, 'ntw'],
        )

    @staticmethod
    def id() -> IndexedBase:
        """Symbol"""
        return IndexedBase('emit^setup')
