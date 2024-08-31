"""Storage - Stashes Resource to Withdraw Later
"""

from dataclasses import dataclass, fields

from ...elements.parameters.balances.inventory import Inventory
from .._attrs._balances import _StgBalance
from .._attrs._birthing import _StgBirthing
from .._attrs._bounds import _OpnBounds, _StgBounds
from .._attrs._exacts import _StgExacts
from .._attrs._spatials import LocCollection
from ._birther import _Birther

# Associated Program Elements:
#   Bound Parameters - CapBound, OprBound
#   Exact Parameters - StpEmission, StpExpense, OprExpense, Usage
#   Balance Parameters - Inventory
#   Variable (Transact) - TransactOpr, TransactStp
#   Variable (Emissions) - EmitStp, EmitUse
#   Variable (Losses) - Lose
#   Variable (Operate) - Operate
#   Variable (Use) - Use
#   Variable (Rates) - Rate


@dataclass
class Storage(
    _StgBalance,
    _OpnBounds,
    _StgBounds,
    _StgBirthing,
    _StgExacts,
    LocCollection,
    _Birther,
):
    """Storage stores and withdraws Resources
    There could be a dependent Resource

    A ResourceStg is generate internally as the stored Resource
    Charging and discharging Processes are also generated internally
    Capacity in this case is the amount of Resource that can be stored
    Charging and discharging capacities can also be provided

    Attributes:
        capacity (IsBnd): bound on the capacity of the Operation
        store: (IsBnd): bound by Capacity. Reported by operate as well.
        land_use (IsExt): land use per Capacity
        material_use (IsExt): material use per Capacity
        capex (IsInc): capital expense per Capacity
        opex (IsInc): operational expense based on Operation
        land_use_emission (IsExt): emission due to land use
        material_use_emission (IsExt): emission due to material use
        setup_emission (IsExt): emission due to construction activity
        inventory: (IsBlc): balance needed for storage. can just be a Resource as well
        freight_loss: (IsExt): loss of resource in storage
        capacity_c (IsBnd): bounds for capacity of generated charging Process
        capacity_d (IsBnd): bounds for capacity of generated discharging Process
        locations (list[Location]): Locations where the Storage is located
        basis (str): basis of the component
        citation (dict): citation of the component
        block (str): block of the component
        introduce (str): index in scale when the component is introduced
        retire (str): index in scale when the component is retired
        label (str): label of the component
    """

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
    def inputs():
        """Input attributes"""
        return [
            f.name for f in fields(_OpnBounds) + fields(_StgBounds) + fields(_StgExacts)
        ]

    @property
    def balance(self):
        """Balance of the Storage"""
        return self.inventory

    def inventorize(self):
        """Makes the inventory"""
        if not isinstance(self.inventory, Inventory):
            self.inventory = Inventory(inventory=self.inventory, storage=self)
            self._balanced = True
