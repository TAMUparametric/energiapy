"""Defined Emission Parameters 
"""

from dataclasses import dataclass

from sympy import IndexedBase

from ._parameter import _Parameter


@dataclass
class EmitBnd(_Parameter):
    """Bound on Emission"""

    def __post_init__(self):
        _Parameter.__post_init__(self)

    @property
    def id(self) -> str:
        """Symbol"""
        return IndexedBase('Emit')


@dataclass
class ResEmitBuy(_Parameter):
    """Resource Emission Buy"""

    def __post_init__(self):
        _Parameter.__post_init__(self)

    @property
    def id(self) -> str:
        """Symbol"""
        return IndexedBase('Emit^buy')


@dataclass
class ResEmitSell(_Parameter):
    """Resource Emission Sell"""

    def __post_init__(self):
        _Parameter.__post_init__(self)

    @property
    def id(self) -> str:
        """Symbol"""
        return IndexedBase('Emit^sell')


@dataclass
class ResEmitLoss(_Parameter):
    """Resource Emission Loss"""

    def __post_init__(self):
        _Parameter.__post_init__(self)

    @property
    def id(self) -> str:
        """Symbol"""
        return IndexedBase('Emit^loss')


@dataclass
class CmdEmitUse(_Parameter):
    """Commodity Emission Use"""

    def __post_init__(self):
        _Parameter.__post_init__(self)

    @property
    def id(self) -> str:
        """Symbol"""
        return IndexedBase('Emit^use')


@dataclass
class OpnEmit(_Parameter):
    """Emission due to setting up operation"""

    def __post_init__(self):
        _Parameter.__post_init__(self)

    @property
    def id(self) -> str:
        """Symbol"""
        return IndexedBase('Emit^opn')
