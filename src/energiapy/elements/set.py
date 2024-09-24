"""A set of objects"""

from __future__ import annotations

from dataclasses import dataclass, field
from operator import is_
from typing import TYPE_CHECKING, Self
from ..core._handy._dunders import _Dunders
from sympy import Symbol


if TYPE_CHECKING:
    from ..components.commodity.cash import Cash
    from ..components.commodity.emission import Emission
    from ..components.commodity.land import Land
    from ..components.commodity.resource import Resource
    from ..components.operation.process import Process
    from ..components.operation.storage import Storage
    from ..components.operation.transit import Transit


@dataclass
class Set(_Dunders):
    """A Set"""

    name: str = field(default='set')
    members: (
        int | set[str | Cash | Emission | Land | Resource | Process | Storage | Transit]
    ) = field(default=None)
    attr: str = field(default=None)

    def __post_init__(self):
        self.name = f'{self.name}_{self.attr}'
        if isinstance(self.members, int):
            self.members = [f'{self.name}_{i}' for i in range(self.members)]

    @property
    def sym(self) -> Symbol:
        """symbolic representation"""
        return Symbol(f'{self.name}^{self.attr}')

    def __add__(self, other: Self):
        if isinstance(other, Set):
            return Set(self.members | other.members, attr=f'{self.attr}|{other.attr}')

    def __sub__(self, other: Self):
        if isinstance(other, Set):
            return Set(self.members - other.members, attr=f'{self.attr}-{other.attr}')

    def __mul__(self, other: Self):
        if isinstance(other, Set):
            return Set(self.members & other.members, attr=f'{self.attr}&{other.attr}')

    def __truediv__(self, other: Self):
        if isinstance(other, Set):
            return Set(self.members ^ other.members, attr=f'{self.attr}^{other.attr}')

    def __eq__(self, other: Self):
        if isinstance(other, Set):
            return is_(self, other)
