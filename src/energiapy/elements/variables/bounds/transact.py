"""Variables for Transact
"""

from dataclasses import dataclass

from sympy import IndexedBase

from ...components.commodity.cash import Cash
from ...components.commodity.land import Land
from ...components.commodity.material import Material
from ...components.operation.process import Process
from ...components.operation.storage import Storage
from ...components.operation.transit import Transit
from ..disposition.structure import make_structures
from ._variable import _BoundVar, _ExactVar
from .boundbounds.operate import Operate
from .bounds.capacitate import Capacitate
from .bounds.trade import Buy, Sell
from .use import Use

# ---------------MixIns---------------


@dataclass
class _Transact(_BoundVar):
    """Transact is the cost of a Component
    This is a parent class
    """

    def __post_init__(self):
        _BoundVar.__post_init__(self)

    @classmethod
    def structures(cls, component):
        """The allowed structures of disposition of the Variable"""
        return make_structures(csh_strict=True, spt=['loc', 'lnk', 'ntw'])

    @classmethod
    def parent(cls):
        """The Parent Task of the Variable"""

    @classmethod
    def child(cls):
        """The Parent Variable doesnot carry Child Component"""


@dataclass
class _Exp(_ExactVar):
    """Transact is the cost of a Component
    This is a parent class
    """

    def __post_init__(self):
        _ExactVar.__post_init__(self)

    @classmethod
    def child(cls):
        """The Parent Variable doesnot carry Child Component"""
        return Cash


@dataclass
class _ExpTrade(_Exp):
    """Resource Transact
    This is a parent class
    """

    def __post_init__(self):
        _Exp.__post_init__(self)

    @classmethod
    def structures(cls, component):
        """The allowed structures of disposition of the Variable"""
        return make_structures(
            csh_strict=True, cmd='res', opn='pro', spt=['loc', 'ntw']
        )


@dataclass
class _ExpOpn(_Exp):
    """Capacitate Transact
    This is a parent class
    """

    def __post_init__(self):
        _Exp.__post_init__(self)

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
            csh_strict=True,
            mde=True,
            opn=[opn],
            spt=[spt, 'ntw'],
        )


@dataclass
class _ExpOpnI(_ExpOpn):
    """Incidental Transact for Operation
    This is a parent class
    """

    def __post_init__(self):
        _ExpOpn.__post_init__(self)

    @classmethod
    def parent(cls):
        """The Parent Task of the Variable"""


# -------------Variables---------------


@dataclass
class Spend(_Transact):
    """System Transact"""

    def __post_init__(self):
        _Transact.__post_init__(self)

    @staticmethod
    def id() -> IndexedBase:
        """Symbol"""
        return IndexedBase('spend')


@dataclass
class Earn(_Transact):
    """System Transact"""

    def __post_init__(self):
        _Transact.__post_init__(self)

    @staticmethod
    def id() -> IndexedBase:
        """Symbol"""
        return IndexedBase('earn')


@dataclass
class TransactBuy(_ExpTrade):
    """Buy Transact"""

    def __post_init__(self):
        _ExpTrade.__post_init__(self)

    @classmethod
    def parent(cls):
        """The Parent Task of the Variable"""
        return Buy

    @staticmethod
    def id() -> IndexedBase:
        """Symbol"""
        return IndexedBase('exp^buy')


@dataclass
class TransactSll(_ExpTrade):
    """Sell Transact"""

    def __post_init__(self):
        _ExpTrade.__post_init__(self)

    @classmethod
    def parent(cls):
        """The Parent Task of the Variable"""
        return Sell

    @staticmethod
    def id() -> IndexedBase:
        """Symbol"""
        return IndexedBase('exp^sell')


@dataclass
class TransactPnt(_ExpTrade):
    """Buy Transact"""

    def __post_init__(self):
        _ExpTrade.__post_init__(self)

    @classmethod
    def parent(cls):
        """The Parent Task of the Variable"""
        return Sell

    @staticmethod
    def id() -> IndexedBase:
        """Symbol"""
        return IndexedBase('penalty')


@dataclass
class TransactCrd(_ExpTrade):
    """TransactCrd Earned"""

    def __post_init__(self):
        _ExpTrade.__post_init__(self)

    @classmethod
    def parent(cls):
        """The Parent Task of the Variable"""
        return Sell

    @staticmethod
    def id() -> IndexedBase:
        """Symbol"""
        return IndexedBase('credit')


@dataclass
class TransactUse(_Exp):
    """Use Transact"""

    def __post_init__(self):
        _Exp.__post_init__(self)

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
            csh_strict=True,
            cmd=[cmd],
            opn=['pro', 'stg', 'trn'],
            spt=['loc', 'lnk', 'ntw'],
        )

    @staticmethod
    def id() -> IndexedBase:
        """Symbol"""
        return IndexedBase('exp^use')


@dataclass
class TransactStp(_ExpOpn):
    """Capacitate Transact"""

    def __post_init__(self):
        _ExpOpn.__post_init__(self)

    @classmethod
    def parent(cls):
        """The Parent Task of the Variable"""
        return Capacitate

    @staticmethod
    def id() -> IndexedBase:
        """Symbol"""
        return IndexedBase('capex')


@dataclass
class TransactOpr(_ExpOpn):
    """Operate Transact"""

    def __post_init__(self):
        _ExpOpn.__post_init__(self)

    @classmethod
    def parent(cls):
        """The Parent Task of the Variable"""
        return Operate

    @staticmethod
    def id() -> IndexedBase:
        """Symbol"""
        return IndexedBase('opex')


@dataclass
class TransactStpI(_ExpOpnI):
    """Incidental Capital Transact"""

    def __post_init__(self):
        _ExpOpnI.__post_init__(self)

    @staticmethod
    def id() -> IndexedBase:
        """Symbol"""
        return IndexedBase('capex^I')


@dataclass
class TransactOprI(_ExpOpnI):
    """Incidental Operational Transact"""

    def __post_init__(self):
        _ExpOpnI.__post_init__(self)

    @staticmethod
    def id() -> IndexedBase:
        """Symbol"""
        return IndexedBase('opex^I')
