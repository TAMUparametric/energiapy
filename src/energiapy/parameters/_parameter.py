"""Defined Parameters 
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .._core._handy._dunders import _Dunders

if TYPE_CHECKING:
    from .._core._aliases._is_value import IsValue


@dataclass
class _Parameter(_Dunders, ABC):
    """Model Parameter

    Attributes:
        value (IsValue): The value of the parameter. Can be Constant, M, Theta, DataSet
    """

    value: IsValue = field(default=None)

    def __post_init__(self):
        self.disposition = self.value.disposition
        self.name = str(self.sym)

    @staticmethod
    @abstractmethod
    def id() -> str:
        """Symbolic representation of the Parameter"""

    @staticmethod
    def collection():
        """What collection the element belongs to"""
        return 'parameters'

    @property
    def sym(self):
        """Symbol"""
        return self.id()[self.disposition.sym]
