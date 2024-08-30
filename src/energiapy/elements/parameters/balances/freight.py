"""Freight Conversion for Transit Operation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ._balance import _Balance

if TYPE_CHECKING:
    from ...core.aliases.iscmp import IsTransit
    from ...core.aliases.isinp import IsBalInput


@dataclass
class Freight(_Balance):
    """Inventory Balance for Storage

    Attributes:
        freight (IsBalInput): The freight balance.
        storage (IsStorage): The transity component.
    """

    freight: IsBalInput = field(default=None)
    transit: IsTransit = field(default=None)

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
