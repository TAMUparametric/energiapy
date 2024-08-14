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
class ExpBnd(_Parameter):
    """Expense Cap"""

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
