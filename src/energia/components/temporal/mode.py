"""Operational Mode attached to a Parameter"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from sympy import Symbol

from ...core._handy._dunders import _Dunders

if TYPE_CHECKING:
    from ..task.process import Process
    from ..task.storage import Storage
    from ..task.transport import Transport


@dataclass
class X(_Dunders):
    """Represents a discrete choice to be taken within a
    spatiotemporal disposition.
    Modes can split you
    Mode of Operation, can be used for Conversion, Use, etc.

    Attributes:
        name (str, float, int]): The name of the mode, usually a number.
    """

    name: str | float | int = field(default=None)

    def __post_init__(self):
        self.name = str(f'x_{self.name}')
        # Dummy initial name
        setattr(self, 'sym', Symbol(f'{self.name}'))

    def personalize(self, opn: Process | Storage | Transport, attr: str):
        """Personalizes the operational mode
        adds the name of the operation
        and first three letters of the attribute
        """
        x = Symbol(f'{self.name}^{attr[0]}{attr[-1]}_{opn.name}')
        setattr(self, 'sym', x)
        self.name = str(x)
        return self

    @property
    def sym(self):
        """Symbol"""
        return self._sym

    @sym.setter
    def sym(self, new_sym):
        self._sym = new_sym
