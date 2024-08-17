"""Operational Mode
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Union

from ..._core._handy._dunders import _Dunders

if TYPE_CHECKING:
    from ..._core._aliases._is_component import IsOperational


@dataclass
class X(_Dunders):
    """Mode of Operation, can be used for Conversion, Use, etc."""

    name: Union[str, float, int] = field(default=None)

    def __post_init__(self):
        self.name = f'{self.name}'

    def personalize(self, opn: IsOperational, attr: str):
        """Personalizes the operational mode
        adds the name of the operation and for what input
        it is being used for
        """
        self.name = f'x({opn},{attr},{self.name})'
        return self
