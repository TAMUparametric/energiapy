"""Aspect describes the behavior of a component using model elements
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Tuple

from ..core._handy._dunders import _Dunders
from ..core._nirop._error import CacodcarError

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

    @staticmethod
    def collection():
        """What collection the element belongs to"""
        return 'variables'

    @property
    def sym(self):
        """The symbolic representation of the Variable"""
        return self.id()[self.disposition.sym]
