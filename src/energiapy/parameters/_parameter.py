"""Defined Parameters 
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .._core._handy._dunders import _Dunders

if TYPE_CHECKING:
    from .._core._aliases._is_data import IsValue


@dataclass
class _Parameter(_Dunders):
    """Model Parameter"""

    value: IsValue = field(default=None)

    def __post_init__(self):
        self.disposition = self.value.disposition
        self.name = f'{self.id()}|{self.value.name}|'

    @classmethod
    def id(cls):
        """The id of the Parameter"""
        return cls.__name__

    @staticmethod
    def collection():
        """What collection the element belongs to"""
        return 'parameters'
