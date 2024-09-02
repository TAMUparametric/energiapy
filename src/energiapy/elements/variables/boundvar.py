"""General Bounded Variable Class
"""

from dataclasses import dataclass, field

from sympy import IndexedBase

from ._variable import _Variable


@dataclass
class BoundVar(_Variable):
    """BoundVar is a general variable for how much is Bound
    This is a parent class

    Attributes:
        index (Index): Index of the Variable
        component (IsDfn): Component for which variable is being defined
        symbol (IndexedBase): Symbolic representation of the Variable
        p (bool): Does it add to the Balance (plus sign)
        m (bool): Does it subtract from the Balance (minus sign)
        symbol_p (str): Symbol if p is True
        symbol_m (str): Symbol if m is True

    """

    p: bool = field(default=False)
    m: bool = field(default=False)
    symbol_p: str = field(default=None)
    symbol_m: str = field(default=None)

    def __post_init__(self):
        _Variable.__post_init__(self)

        if not self.p and not self.m:
            raise ValueError(f'{self}: p or m must be True')

        if self.p and self.m:
            raise ValueError(f'{self}: p and m cannot be both True')

        if self.p and not self.symbol_p:
            raise ValueError(f'{self}: symbol_p must be provided')

        if self.m and not self.symbol_m:
            raise ValueError(f'{self}: symbol_m must be provided')

    @property
    def symib(self) -> IndexedBase:
        """Symbolic representation of the Variable"""
        if self.p:
            return IndexedBase(self.symbol_p)
        else:
            return IndexedBase(self.symbol_m)
