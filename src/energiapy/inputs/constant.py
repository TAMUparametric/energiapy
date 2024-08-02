from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .bounds import Certainty, VarBnd
from .value import Value

if TYPE_CHECKING:
    from ..type.alias import IsNumeric


@dataclass
class Constant(Value):
    """Value as a numberic input

    Args:
        number (IsNumeric): numeric input
    """
    number: IsNumeric = field(default=None)

    def __post_init__(self):
        Value.__post_init__(self)
        self.name = f'{self.number}'

        self._certainty, self._approach, self._varbound = Certainty.CERTAIN, None, VarBnd.EXACT

    # TODO: add __lt__, __gt__, __eq__, __ne__, __le__, __ge__ methods

    @property
    def value(self) -> IsNumeric:
        """Returns a number 
        """
        return self.number
