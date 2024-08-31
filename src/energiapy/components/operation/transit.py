"""Transit moves Resources between Locations
"""

from dataclasses import dataclass, fields

from ...elements.parameters.balances.freight import Freight
from .._attrs._balances import _TrnBalance
from .._attrs._bounds import _OpnBounds, _ResLnkBounds, _TrnBounds
from .._attrs._exacts import _TrnExacts
from .._attrs._spatials import LnkCollection
from ._birther import _Birther

# Associated Program Elements:
#   Bound Parameters - CapBound, OprBound
#   Exact Parameters - StpEmission, StpExpense, OprExpense, Usage
#   Balance Parameters - Freight
#   Variable (Transact) - TransactOpr, TransactStp
#   Variable (Emissions) - EmitStp, EmitUse
#   Variable (Losses) - Lose
#   Variable (Operate) - Operate
#   Variable (Trade) - Ship
#   Variable (Use) - Use
#   Variable (Rates) - Rate


@dataclass
class Transit(
    _TrnBalance,
    _OpnBounds,
    _TrnBounds,
    _TrnExacts,
    _ResLnkBounds,
    LnkCollection,
    _Birther,
):
    """Transit moves Resources between Locations through a Linkage
    There could be a dependent Resource

    A ResourceTrn is generate internally as the stored Resource
    Loading and Unloading Processes are also generated internally
    Capacity in this case is the amount of Resource that can be Transported
    Loading and Unloading capacities are the same as Transit Capacity

    Attributes:
        capacity (IsBnd): bound on the capacity of the Operation
        transport (IsBnd): bound by Capacity. Reported by operate as well.
        land_use (IsExt): land use per Capacity
        material_use (IsExt): material use per Capacity
        capex (IsInc): capital expense per Capacity
        opex (IsInc): operational expense based on Operation
        land_use_emission (IsExt): emission due to land use
        material_use_emission (IsExt): emission due to material use
        setup_emission (IsExt): emission due to construction activity
        freight (IsBlc): balance of Resources carried by the Operation
        freight_loss: (IsExt): loss of resource during transportation
        linkages (list[IsLinkage]): linkages between which Transit exists
        ship (IsBnd): bound on shipping a Resource
        speed (IsExt): speed of Transit
        basis (str): basis of the component
        citation (dict): citation of the component
        block (str): block of the component
        introduce (str): index in scale when the component is introduced
        retire (str): index in scale when the component is retired
        label (str): label of the component

    """

    def __post_init__(self):
        # ship is a resourcebnd input
        # so it needs to be a dictionary with Resource as key
        # if not provided, use base Resource
        if self.ship:
            # if freight is a dictionary
            # i.e. it has some Resource dependency
            if isinstance(self.freight, dict):
                # use the base Resource as key
                self.ship = {list(self.freight)[0]: self.ship}
            else:
                # else, it is a Resource itself,
                # so use it as key
                self.ship = {self.freight: self.ship}

        _Birther.__post_init__(self)

    @property
    def _operate(self):
        """Returns attribute value that signifies operating bounds"""
        if self.transport:
            return self.transport
        else:
            return [1]

    @property
    def balance(self):
        """Balance attribute"""
        return self.freight

    @property
    def capacity_in(self):
        """Capacity of the Loading Process"""
        # Returns og input if birthing is not done
        # This is because the birthed Process capacity
        # needs to be set
        if self._birthed:
            return self.capacity
        else:
            return self.capacity.og_input

    @property
    def capacity_out(self):
        """Capacity of the Unloading Process"""
        # Returns og input if birthing is not done
        # This is because the birthed Process capacity
        # needs to be set
        if self._birthed:
            return self.capacity
        else:
            return self.capacity.og_input

    @staticmethod
    def inputs():
        """Input attributes"""
        return [
            f.name
            for f in fields(_OpnBounds)
            + fields(_TrnBounds)
            + fields(_TrnExacts)
            + fields(_ResLnkBounds)
        ]

    def freightize(self):
        """Makes the freight"""
        if not isinstance(self.freight, Freight):
            self.freight = Freight(freight=self.freight, transit=self)
            self._balanced = True
