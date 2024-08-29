"""Transit moves Resources between Locations
"""

from dataclasses import dataclass, fields

from ...attrs.balances import TrnBalance
from ...attrs.bounds import OpnBounds, ResLnkBounds, TrnBounds
from ...attrs.exacts import TrnExacts
from ...attrs.spatials import LnkCollection
from ...parameters.balances.freight import Freight
from ._birther import _Birther


@dataclass
class Transit(
    TrnBalance, OpnBounds, TrnBounds, TrnExacts, ResLnkBounds, LnkCollection, _Birther
):
    """Transit moves Resources between Locations through a Linkage
    There could be a dependent Resource

    A ResourceTrn is generate internally as the stored Resource
    Loading and Unloading Processes are also generated internally
    Capacity in this case is the amount of Resource that can be Transported
    Loading and Unloading capacities are the same as Transit Capacity

    Attributes:
        capacity (IsBoundInput): bound on the capacity of the Operation
        land (IsExactInput): land use per Capacity
        material (IsExactInput): material use per Capacity
        capex (IsExactInput): capital expense per Capacity
        opex (IsExactInput): operational expense based on Operation
        emission (IsExactInput): emission due to construction per Capacity
        loss: (IsExactInput): loss of resource during transportation
        freight (IsBalInput): Resource carried by the Operation
        transport (IsBoundInput): bound by Capacity. Reported by operate as well.
        linkages (List[IsLinkage]): linkages between which Transit exists
        ship (IsBoundInput): bound on shipping a Resource
        speed (IsExactInput): speed of Transit
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
            for f in fields(OpnBounds)
            + fields(TrnBounds)
            + fields(TrnExacts)
            + fields(ResLnkBounds)
        ]

    def freightize(self):
        """Makes the freight"""
        if not isinstance(self.freight, Freight):
            self.freight = Freight(freight=self.freight, transit=self)
            self._balanced = True
