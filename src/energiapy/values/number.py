from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .value import Value

if TYPE_CHECKING:
    from ..type.alias import IsNumeric


@dataclass
class Number(Value):
    """Value as a numberic input

    Args:
        number (IsNumeric): numeric input
    """
    number: IsNumeric = field(default=None)

    def __post_init__(self):
        self.name = f'{self.number}'

    @property
    def value(self) -> IsNumeric:
        """Returns a number 
        """
        return self.number
