"""Defined Parameters 
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .._core._handy._dunders import _Dunders

if TYPE_CHECKING:
    from .._core._aliases._is_data import IsData


@dataclass
class _Parameter(_Dunders):
    """Model Parameter"""

    value: IsData = field(default=None)

    def __post_init__(self):
        self.dispostion = self.value.disposition
        self.name = f'{self.id()}{self.value.name}'

    @classmethod
    def id(cls):
        """The id of the task"""
        return cls.__name__
