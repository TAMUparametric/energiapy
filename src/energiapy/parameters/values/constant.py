from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from sympy import IndexedBase

from ..defined.enums import Certainty
from ._value import _Value

if TYPE_CHECKING:
    from ...core.aliases.is_input import IsNumeric


@dataclass
class Constant(_Value):
    """Value as a numberic input

    Args:
        number (IsNumeric): numeric input
    """

    constant: IsNumeric = field(default=None)

    def __post_init__(self):
        _Value.__post_init__(self)

        self._certainty, self._approach = Certainty.CERTAIN, None

    @property
    def value(self) -> IsNumeric:
        """Returns a number"""
        return self.constant

    @property
    def id(self):
        """Symbol"""
        return IndexedBase(f'{self.value}')

    # Constant compare by the value of the number
    def __gt__(self, other):
        if isinstance(other, (int, float)):
            return self.constant > other
        if isinstance(other, Constant):
            return self.constant > other.constant
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, (int, float)):
            return self.constant < other
        if isinstance(other, Constant):
            return self.constant < other.constant
        return NotImplemented
