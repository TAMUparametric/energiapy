"""Aspect describes the behavior of a component using model elements
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .._core._handy._dunders import _Dunders
from .._core._nirop._error import CacodcarError

if TYPE_CHECKING:
    from .._core._aliases._is_block import IsDisposition
    from .._core._aliases._is_variable import IsTask


@dataclass
class _Task(_Dunders, ABC):
    """Component Task"""

    disposition: IsDisposition = field(default=None)

    def __post_init__(self):
        self.name = f'{self._id()}{self.disposition}'

        if not self.disposition.structure() in self._structures():
            raise CacodcarError(
                f'{self}:{self.disposition.structure()} not in {self._structures()}'
            )

    @classmethod
    def _id(cls):
        """The id of the task"""
        return cls.__name__

    @classmethod
    @abstractmethod
    def _structures(cls):
        """The allowed structures of disposition of the task"""

    @staticmethod
    @abstractmethod
    def _parent() -> IsTask:
        """The Parent Task of the task"""
