"""Aspect describes the behavior of a component using model elements
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Tuple

from ..core._handy._dunders import _Dunders
from ..core.nirop.errors import CacodcarError

if TYPE_CHECKING:
    from sympy import IndexedBase

    from ..core.aliases.is_block import IsDisposition
    from ..core.aliases.is_component import IsComponent
    from ..core.aliases.is_variable import IsVariable


@dataclass
class _Variable(_Dunders, ABC):
    """Component Task"""

    disposition: IsDisposition = field(default=None)
    component: IsComponent = field(default=None)

    def __post_init__(self):
        self.name = str(self.sym)

        if not self.disposition.structure() in self.structures(self.component):
            raise CacodcarError(
                f'{self}:{self.disposition.structure()} not in {self.structures(self.component)}'
            )

    @staticmethod
    @abstractmethod
    def id() -> IndexedBase:
        """Symbolic representation of the Variable"""

    @classmethod
    @abstractmethod
    def structures(cls, component) -> List[Tuple[str]]:
        """The allowed structures of Dispositions of the Variable"""

    @classmethod
    @abstractmethod
    def parent(cls) -> IsVariable:
        """The Parent Variable of the Variable"""

    @classmethod
    @abstractmethod
    def child(cls) -> IsComponent:
        """The Parent Variable doesnot carry Child Component"""

    @property
    def sym(self):
        """The symbolic representation of the Variable"""
        return self.id()[self.disposition.sym]


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
