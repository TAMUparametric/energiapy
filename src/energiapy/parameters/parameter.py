"""Defined Parameters 
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .._core._handy._dunders import _Dunders

if TYPE_CHECKING:
    from .._core._aliases._is_data import IsData


@dataclass
class _Parameter(_Dunders):
    """Model Parameter"""

    value: IsData = field(default=None)

    def __post_init__(self):
        self.dispostion = self.value.disposition
        self.name = f'{self._id()}{self.value.name}'

    @classmethod
    def _id(cls):
        """The id of the task"""
        return cls.__name__


@dataclass
class BuyBnd(_Parameter):
    """Buy Bounds"""

    def __post_init__(self):
        _Parameter.__post_init__(self)


@dataclass
class SellBnd(_Parameter):
    """Sell Bounds"""

    def __post_init__(self):
        _Parameter.__post_init__(self)


@dataclass
class CmdUse(_Parameter):
    """Commodity Use"""

    def __post_init__(self):
        _Parameter.__post_init__(self)


@dataclass
class ExpBnd(_Parameter):
    """Expense Cap"""

    def __post_init__(self):
        _Parameter.__post_init__(self)


@dataclass
class BuyPrice(_Parameter):
    """Resource Buy Price"""

    def __post_init__(self):
        _Parameter.__post_init__(self)


@dataclass
class SellPrice(_Parameter):
    """Resource Sell Price"""

    def __post_init__(self):
        _Parameter.__post_init__(self)


@dataclass
class ResPenalty(_Parameter):
    """Resource Penalty Price"""

    def __post_init__(self):
        _Parameter.__post_init__(self)


@dataclass
class ResCredit(_Parameter):
    """Resource Buy Price"""

    def __post_init__(self):
        _Parameter.__post_init__(self)


@dataclass
class UseExp(_Parameter):
    """Resource Use Expense"""

    def __post_init__(self):
        _Parameter.__post_init__(self)


@dataclass
class CapExp(_Parameter):
    """Operation Capital Expense"""

    def __post_init__(self):
        _Parameter.__post_init__(self)


@dataclass
class OpExp(_Parameter):
    """Operational Expense"""

    def __post_init__(self):
        _Parameter.__post_init__(self)


@dataclass
class ResLoss(_Parameter):
    """Resource Loss"""

    def __post_init__(self):
        _Parameter.__post_init__(self)


@dataclass
class CapBnd(_Parameter):
    """Capacity Bounds"""

    def __post_init__(self):
        _Parameter.__post_init__(self)
