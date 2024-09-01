"""Aspect describes the behavior of a component using model elements
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from sympy import IndexedBase

from ...core._handy._dunders import _Dunders
from ...core.aliases.cmps.isdfn import IsDfn
from ...core.nirop.errors import CacodcarError

if TYPE_CHECKING:
    from ..disposition.index import Index


@dataclass
class _Variable(_Dunders, ABC):
    """Component Task"""

    index: Index = field(default=None)
    component: IsDfn = field(default=None)

    def __post_init__(self):
        self.name = str(self.sym)

        if not self.index.structure() in self.structures(self.component):
            raise CacodcarError(
                f'{self}:{self.index.structure()} not in {self.structures(self.component)}'
            )

    @staticmethod
    @abstractmethod
    def id() -> IndexedBase:
        """Symbolic representation of the Variable"""

    @classmethod
    @abstractmethod
    def structures(cls, component) -> list[tuple[str]]:
        """The allowed structures of Indexs of the Variable"""

    @classmethod
    @abstractmethod
    def parent(cls) -> _Variable:
        """The Parent Variable of the Variable"""

    @classmethod
    @abstractmethod
    def child(cls) -> IsDfn:
        """The Parent Variable doesnot carry Child Component"""

    @property
    def sym(self):
        """The symbolic representation of the Variable"""
        return self.id()[self.index.sym]


# The ones below are made for the sake of clarity
# They are the same otherwise
# That being said, the parents of exacts are usually BoundVars
# The parents of bounds are usually BoundVars or BinaryVars


@dataclass
class _BoundVar(_Variable):
    """Bound is a general variable for how much is Bound
    This is a parent class
    """

    def __post_init__(self):
        _Variable.__post_init__(self)


@dataclass
class _ExactVar(_Variable):
    """Exact is a general variable for how much is Exact
    This is a parent class
    """

    def __post_init__(self):
        _Variable.__post_init__(self)
