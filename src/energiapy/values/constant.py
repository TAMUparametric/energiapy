from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ._approach import _Certainty
from ._bounds import _VarBnd
from ._value import _Value

if TYPE_CHECKING:
    from .._core._aliases._is_input import IsNumeric


@dataclass
class Constant(_Value):
    """Value as a numberic input

    Args:
        number (IsNumeric): numeric input
    """

    constant: IsNumeric = field(default=None)

    def __post_init__(self):
        _Value.__post_init__(self)

        self.name = f'{self.constant}{self.name}'

        if self._varbnd is None:
            self._varbnd = _VarBnd.EXACT

        self._certainty, self._approach = _Certainty.CERTAIN, None

    @property
    def value(self) -> IsNumeric:
        """Returns a number"""
        return self.constant

    @staticmethod
    def collection():
        """reports what collection the component belongs to"""
        return 'constants'

    @staticmethod
    def _id():
        """ID to add to name"""
        return ''

    def __gt__(self, other):
        if isinstance(other, (int, float)):
            # BigM is always greater than any number
            return self.constant > other
        if isinstance(other, Constant):
            return self.constant > other.constant
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, (int, float)):
            # BigM is always greater than any number
            return self.constant < other
        if isinstance(other, Constant):
            return self.constant < other.constant
        return NotImplemented
