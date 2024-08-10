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
        self.name = f'{self.constant}'

        self._certainty, self._approach, self._varbound = (
            _Certainty.CERTAIN,
            None,
            _VarBnd.EXACT,
        )

    # TODO: add __lt__, __gt__, __eq__, __ne__, __le__, __ge__ methods

    @property
    def value(self) -> IsNumeric:
        """Returns a number"""
        return self.constant
