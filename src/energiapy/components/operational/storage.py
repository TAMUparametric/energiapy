"""Storage - Stashes Resource to Withdraw Later
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List

from ...parameters.balances.inventory import Inventory
from ._birther import _Birther


if TYPE_CHECKING:
    from ..._core._aliases._is_component import IsLocation
    from ..._core._aliases._is_input import IsBoundInput, IsExactInput, IsBalInput


@dataclass
class Storage(_Birther):
    """Storage stores and withdraws Resources
    There could be a dependent Resource

    A ResourceStg is generate internally as the stored Resource
    Charging and discharging Processes are also generated internally
    Capacity in this case is the amount of Resource that can be stored
    Charging and discharging capacities can also be provided

    Attributes:
        capacity (IsBoundInput): bound on the capacity of the Operation
        land (IsExactInput): land use per Capacity
        material (IsExactInput): material use per Capacity
        capex (IsExactInput): capital expense per Capacity
        opex (IsExactInput): operational expense based on Operation
        emission (IsExactInput): emission due to construction per Capacity
        loss: (IsExactInput): loss of resource in storage
        store: (IsBoundInput): bound by Capacity. Reported by operate as well.
        inventory: (IsBalInput): balance needed for storage. can just be a Resource as well
        capacity_c (IsBoundInput): bounds for capacity of generated charging Process
        capacity_d (IsBoundInput): bounds for capacity of generated discharging Process
        basis (str): basis of the component
        citation (dict): citation of the component
        block (str): block of the component
        introduce (str): index in scale when the component is introduced
        retire (str): index in scale when the component is retired
        label (str): label of the component
    """

    loss: IsExactInput = field(default=None)
    store: IsBoundInput = field(default=None)
    inventory: IsBalInput = field(default=None)
    locations: List[IsLocation] = field(default=None)
    capacity_in: IsBoundInput = field(default=None)
    capacity_out: IsBoundInput = field(default=None)

    def __post_init__(self):
        _Birther.__post_init__(self)

    @property
    def _operate(self):
        """Returns attribute value that signifies operating bounds"""
        if self.store:
            return self.store
        else:
            return [1]

    @staticmethod
    def _spatials():
        """Spatial Components where the Operation is located"""
        return 'locations'

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

    @property
    def balance(self):
        """Balance of the Storage"""
        return self.inventory

    def inventorize(self):
        """Makes the inventory"""
        if not isinstance(self.inventory, Inventory):
            self.inventory = Inventory(inventory=self.inventory, storage=self)
            self._balanced = True
