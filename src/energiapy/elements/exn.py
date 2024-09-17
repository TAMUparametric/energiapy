"""Expression 
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Self
from dataclasses import dataclass, field

from ..core._handy._dunders import _Reprs
from .cns import Cns

if TYPE_CHECKING:
    from .prm import Prm
    from .vrb import Vrb


@dataclass
class Exn(_Reprs):
    """Provides some relational operation between Parameters and Variables

    Attributes:
        prm1 (Parameter): First Parameter
        component (IsDfn): Component for which variable is being defined
        symbol (IndexedBase): Symbolic representation of the Variable
    """

    one: Prm | Vrb | Self = field()
    two: Prm | Vrb | Self = field()
    rel: str = field()
    name: str = field(default='Exn')

    @property
    def sym(self):
        """symbolic representation"""
        if self.rel == '+':
            return self.one.sym + self.two.sym 
        
        if self.rel == '-':
            return self.one.sym - self.two.sym
        
        if self.rel == '*':
            return self.one.sym* self.two.sym
        
        if self.rel == '/':
            return self.one.sym / self.two.sym

    def __add__(self, other: Self | Prm | Vrb):
        return Exn(one=self, two=other, rel='+')

    def __sub__(self, other: Self | Prm | Vrb):
        return Exn(one=self, two=other, rel='-')

    def __mul__(self, other: Self | Prm | Vrb):
        return Exn(one=self, two=other, rel='*')

    def __truediv__(self, other: Self | Prm | Vrb):
        return Exn(one=self, two=other, rel='/')

    def __eq__(self, other: Self | Prm | Vrb):
        return Cns(lhs=self, rhs=other, rel='eq')

    def __le__(self, other: Self | Prm | Vrb):
        return Cns(lhs=self, rhs=other, rel='leq')

    def __ge__(self, other: Self | Prm | Vrb):
        return Cns(lhs=self, rhs=other, rel='geq')

    def __lt__(self, other: Self | Prm | Vrb):
        return self <= other

    def __gt__(self, other: Self | Prm | Vrb):
        return self >= other


