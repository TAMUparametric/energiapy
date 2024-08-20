"""Storage - Stashes Resource to Withdraw Later
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List

from ...parameters.balance.inventory import Inventory
from ._operational import _Operational

# import operator
# from functools import reduce


if TYPE_CHECKING:
    from ..._core._aliases._is_component import IsLocation
    from ..._core._aliases._is_input import (IsBoundInput, IsExactInput,
                                             IsInvInput)


@dataclass
class Storage(_Operational):
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
        inventory: (IsInvInput): balance needed for storage. can just be a Resource as well
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
    inventory: IsInvInput = field(default=None)
    locations: List[IsLocation] = field(default=None)
    capacity_c: IsBoundInput = field(default=None)
    capacity_d: IsBoundInput = field(default=None)

    def __post_init__(self):
        _Operational.__post_init__(self)

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

    def inventorize(self):
        """Makes the inventory"""
        if not isinstance(self.inventory, Inventory):
            self.inventory = Inventory(inventory=self.inventory, storage=self)

    @property
    def processes(self):
        """Processes in Storage"""
        return self._processes

    @processes.setter
    def processes(self, processes):
        """Set Processes"""
        self._processes = processes

    @property
    def process_c(self):
        """Process from Resource to ResourceStg"""
        return self.processes[0]

    @property
    def process_d(self):
        """Process from ResourceStg to Resource"""
        return self.processes[1]

    @property
    def conversion_c(self):
        """Conversion from Resource to ResourceStg"""
        return getattr(self.system, self.name).process_c.conversion

    @property
    def conversion_d(self):
        """Conversion from ResourceStg to Resource"""
        return self.process_d.conversion

    @property
    def balance_c(self):
        """Balance from Resource to ResourceStg"""
        return self.conversion_c.balance

    @property
    def balance_d(self):
        """Balance from ResourceStg to Resource"""
        return self.conversion_d.balance

    @property
    def resources(self):
        """Resources in Inventory"""
        return sorted(set(self.conversion_c.involved))
