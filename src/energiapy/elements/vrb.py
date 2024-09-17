"""General Variable Class
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Self, TYPE_CHECKING
from sympy import IndexedBase, Symbol

from ..core._handy._dunders import _Reprs
from .disposition.index import Index
from .exn import Exn
from .cns import Cns

if TYPE_CHECKING:
    from ..components.analytical.player import Player
    from ..components.commodity.cash import Cash
    from ..components.commodity.emission import Emission
    from ..components.commodity.land import Land
    from ..components.commodity.resource import Resource
    from ..components.operation.process import Process
    from ..components.operation.storage import Storage
    from ..components.operation.transit import Transit


@dataclass
class Vrb(_Reprs):
    """This is a general Variable

    Attributes:
        index (Index): Index of the Variable
        component (IsDfn): Component for which variable is being defined
        symbol (IndexedBase): Symbolic representation of the Variable
    """

    component: (
        Player | Cash | Emission | Land | Resource | Process | Storage | Transit
    ) = field(default=None)
    index: Index = field(default=None)
    name: str = field(default='vrb')

    @property
    def sym(self) -> IndexedBase:
        """symbolic representation"""
        if self.index:
            return IndexedBase(self.name)[self.index.sym]
        else:
            return Symbol(self.name)

    def args(self):
        """Arguments of the Variable"""
        return {'index': self.index, 'component': self.component}

    def __len__(self):
        if self.index:
            return len(self.index)
        else:
            return 1

    def __add__(self, other: Self | Exn):

        return Exn(one=self, two=other, rel='+')

    def __sub__(self, other: Self | Exn):

        return Exn(one=self, two=other, rel='-')

    def __mul__(self, other: Self | Exn):

        return Exn(one=self, two=other, rel='*')

    def __truediv__(self, other: Self | Exn):

        return Exn(one=self, two=other, rel='/')

    def __eq__(self, other):
        return Cns(lhs=self, rhs=other, rel='eq')

    def __le__(self, other):
        return Cns(lhs=self, rhs=other, rel='leq')

    def __ge__(self, other):
        return Cns(lhs=self, rhs=other, rel='geq')

    def __lt__(self, other):
        return self <= other

    def __gt__(self, other):
        return self >= other
