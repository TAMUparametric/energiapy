"""Operational Mode
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Union, TYPE_CHECKING

from .._core._handy._dunders import _Dunders

if TYPE_CHECKING:
    from .._core._aliases._is_component import IsOperational


@dataclass
class X(_Dunders):
    """Mode of Operation, can be used for Conversion, Use, etc."""

    name: Union[str, float, int] = field(default=None)

    def personalize(self, opn: IsOperational, attr: str):
        """Personalizes the operational mode
        adds the name of the operation and for what input
        it is being used for
        """
        self.name = f'X|{opn},{attr}|{self.name}'
