"""Freight Conversion for Transit Operation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ....core.isalias.inps.isblc import IsBlc
from ._balance import _Balance

if TYPE_CHECKING:
    from ....components.operation.transit import Transit


@dataclass
class Freight(_Balance):
    """Inventory Balance for Storage

    Attributes:
        freight (IsBlc): The freight balance.
        storage (IsStorage): The transity component.
    """

    freight: IsBlc = field(default=None)
    transit: Transit = field(default=None)

    def __post_init__(self):
        _Balance.__post_init__(self)

    @property
    def balance(self):
        """Returns the Inventory balance"""
        return self.freight

    @property
    def operation(self):
        """Returns the Storage component"""
        return self.transit

    @property
    def conversion_l(self):
        """Loading conversion
        Returns input conversion
        """
        return self.conversion_in

    @property
    def conversion_d(self):
        """Unloading conversion
        Returns output conversion
        """
        return self.conversion_out
