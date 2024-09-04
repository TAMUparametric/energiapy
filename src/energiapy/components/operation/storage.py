"""Storage - Stashes Resource to Withdraw Later
"""

from dataclasses import dataclass, fields

from ...elements.parameters.balances.inventory import Inventory
from .._attrs._balances import _StgBalance
from .._attrs._birthing import _StgBirthing
from .._attrs._bounds import _EmnBounds, _OpnBounds, _StgBounds, _UsdBounds
from .._attrs._exacts import _EmnExacts, _StgExacts, _UsdExacts
from .._attrs._spatials import _LocCollection
from ._birther import _Birther

# Associated Program Elements:
#   Bound Parameters - CapBound, OprBound
#   Exact Parameters - StpEmission, StpExpense, OprExpense, StpUse
#   Balance Parameters - Inventory
#   Variable (Transact) - TransactOpr, TransactStp
#   Variable (Emissions) - EmitStp, EmitUse
#   Variable (Losses) - Lose
#   Variable (Operate) - Operate
#   Variable (Use) - Use
#   Variable (Rates) - Rate


@dataclass
class _Storage(_OpnBounds, _StgBounds, _StgExacts):
    """These are attributes which are original to Storage"""


@dataclass
class _CmdStorage(_UsdExacts, _UsdBounds, _EmnExacts, _EmnBounds):
    """These are Commodity attributes which can be defined at Storage"""


@dataclass
class Storage(
    _StgBalance,
    _Storage,
    _CmdStorage,
    _StgBirthing,
    _LocCollection,
    _Birther,
):
    """Storage stores and withdraws Resources
    There could be a dependent Resource

    A ResourceStg is generate internally as the stored Resource
    Charging and discharging Processes are also generated internally
    Capacitate in this case is the amount of Resource that can be stored
    Charging and discharging capacities can also be provided

    Attributes:
        capacity (IsBnd): bound on the capacity of the Operation
        store: (IsBnd): bound by Capacitate. Reported by operate as well.
        use (IsBnd): bound on amount of Land or Material used by Process
        setup_use (IsExt): Land or Material setup_use per unit capacity
        capex (IsInc): capital expense per Capacitate
        opex (IsInc): operational expense based on Operation
        use_emission (IsExt): emission due to land or Material use
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
        return [f.name for f in fields(_Storage) + fields(_CmdStorage)]

    @property
    def balance(self):
        """Balance of the Storage"""
        return self.inventory

    def inventorize(self):
        """Makes the inventory"""
        if not isinstance(self.inventory, Inventory):
            self.inventory = Inventory(inventory=self.inventory, storage=self)
            self._balanced = True
