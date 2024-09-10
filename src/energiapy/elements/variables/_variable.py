"""General Variable Class
"""

from __future__ import annotations
from typing import TYPE_CHECKING


from dataclasses import dataclass, field
from sympy import IndexedBase
from ...core._handy._dunders import _Dunders
from ...core.isalias.cmps.isdfn import IsDfn

if TYPE_CHECKING:
    from ..disposition.index import Index


@dataclass
class _Variable(_Dunders):
    """This is a general Variable

    Attributes:
        index (Index): Index of the Variable
        component (IsDfn): Component for which variable is being defined
        symbol (IndexedBase): Symbolic representation of the Variable
    """

    index: Index = field(default=None)
    component: IsDfn = field(default=None)
    symbol: str = field(default=None)

    def __post_init__(self):
        self.name = str(self.sym)
        if not self.symbol:
            raise ValueError(f'{self}: symbol must be provided')

    @property
    def symib(self) -> IndexedBase:
        """Symbolic representation of the Variable"""
        return IndexedBase(self.symbol)

    @property
    def sym(self) -> IndexedBase:
        """The symbolic representation of the Variable"""
        return self.symib[self.index.sym]
