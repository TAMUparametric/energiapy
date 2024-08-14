"""Defined Expense Parameters 
"""

from dataclasses import dataclass

from ._parameter import _Parameter


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
