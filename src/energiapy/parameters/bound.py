"""Defined Expense Parameters 
"""

from dataclasses import dataclass

from ._parameter import _Parameter


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
class ShipBnd(_Parameter):
    """Ship Bounds"""

    def __post_init__(self):
        _Parameter.__post_init__(self)


@dataclass
class SpendBnd(_Parameter):
    """Expense Bound on Spending"""

    def __post_init__(self):
        _Parameter.__post_init__(self)


@dataclass
class EarnBnd(_Parameter):
    """Expense Bound on Earning"""

    def __post_init__(self):
        _Parameter.__post_init__(self)


@dataclass
class CapBnd(_Parameter):
    """Capacity Bounds"""

    def __post_init__(self):
        _Parameter.__post_init__(self)


@dataclass
class OpBnd(_Parameter):
    """Operation Bounds
    This one is multiplied by capacity
    """

    def __post_init__(self):
        _Parameter.__post_init__(self)


@dataclass
class UseBnd(_Parameter):
    """Use Bounds"""

    def __post_init__(self):
        _Parameter.__post_init__(self)
