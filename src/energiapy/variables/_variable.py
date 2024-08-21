"""Aspect describes the behavior of a component using model elements
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Tuple

from .._core._handy._dunders import _Dunders
from .._core._nirop._error import CacodcarError

if TYPE_CHECKING:
    from .._core._aliases._is_block import IsDisposition
    from .._core._aliases._is_component import IsComponent
    from .._core._aliases._is_variable import IsVariable
    from sympy import IndexedBase


@dataclass
class _Variable(_Dunders, ABC):
    """Component Task"""

    disposition: IsDisposition = field(default=None)
    component: IsComponent = field(default=None)

    def __post_init__(self):
        self.name = f'{self.id()}{self.disposition}'

        if not self.disposition.structure() in self.structures(self.component):
            raise CacodcarError(
                f'{self}:{self.disposition.structure()} not in {self.structures(self.component)}'
            )

    @staticmethod
    @abstractmethod
    def sym() -> IndexedBase:
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

    @staticmethod
    def collection():
        """What collection the element belongs to"""
        return 'variables'
