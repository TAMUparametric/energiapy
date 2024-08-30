"""If a parameter is incidental
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ...core._handy._dunders import _Dunders

if TYPE_CHECKING:
    from ...core.aliases.isinp import IsIncidental


@dataclass
class I(_Dunders):
    """Incidental Parameter
    This is useful when a Parameteris not dependent on the Parent Variable

    Incidental Capital Expenditure or Fixed Operational Expenditure are examples

    Attributes:
        value (IsIncidental): The incidental value
    """

    value: IsIncidental = field(default=None)

    def __post_init__(self):
        self.name = 'i'
