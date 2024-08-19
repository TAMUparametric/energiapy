"""energiapy.Storage - Stashes Resource to Withdraw Later
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List

from ...parameters.data.inventory import Inventory
from ._operational import _Operational

# import operator
# from functools import reduce


if TYPE_CHECKING:
    from ..._core._aliases._is_component import IsLocation
    from ..._core._aliases._is_input import (IsBoundInput, IsExactInput,
                                             IsInvInput) 


@dataclass
class Storage(_Operational):
    """Storage component

    Args:
        loss: (IsExactInput, optional): Loss of resource in storage. Defaults to None.

    """

    loss: IsExactInput = field(default=None)
    store: IsBoundInput = field(default=None)
    inventory: IsInvInput = field(default=None)
    locations: List[IsLocation] = field(default=None)

    def __post_init__(self):
        _Operational.__post_init__(self)

    @property
    def _operate(self):
        """Returns attribute value that signifies operating bounds"""
        return self.store

    @staticmethod
    def resourcebnds():
        """Attrs that quantify the bounds of the Component"""
        return []

    @staticmethod
    def resourceexps():
        """Attrs that determine resource expenses of the component"""
        return []

    @staticmethod
    def resourceloss():
        """Attrs that determine resource loss of the component"""
        return ['loss']

    def inventorize(self):
        """Makes the inventory"""
        if not isinstance(self.inventory, Inventory):
            self.inventory = Inventory(inventory=self.inventory, storage=self)

    @property
    def conversion_c(self):
        """Conversion from Resource to ResourceStg"""
        return self.inventory.conversion_c

    @property
    def conversion_d(self):
        """Conversion from ResourceStg to Resource"""
        return self.inventory.conversion_d

    @property
    def balance_c(self):
        """Balance from Resource to ResourceStg"""
        return self.inventory.conversion_c.balance

    @property
    def balance_d(self):
        """Balance from ResourceStg to Resource"""
        return self.inventory.conversion_d.balance
