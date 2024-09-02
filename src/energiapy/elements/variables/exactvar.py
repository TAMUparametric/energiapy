"""General Variable Class which are exact calculations
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from sympy import IndexedBase

from ...core.isalias.cmps.isdfn import IsDfn
from ._variable import _Variable

if TYPE_CHECKING:
    from .boundvar import BoundVar


@dataclass
class ExactVar(_Variable):
    """ExactVar is a general variable for how much is Exact
    This is a parent class

    Attributes:
        index (Index): Index of the Variable
        component (IsDfn): Component for which variable is being defined
        symbol (IndexedBase): Symbolic representation of the Variable
        parent (BoundVar): The Parent Variable of the Variable
        child (IsDfn): The Parent Variable doesnot carry Child Component in Index

    """

    parent: BoundVar = field(default=None)
    child: IsDfn = field(default=None)

    def __post_init__(self):
        _Variable.__post_init__(self)

    @property
    def symib(self) -> IndexedBase:
        """Symbolic representation of the Variable"""
        return IndexedBase(self.symbol)
