"""Transit moves Resources between Locations
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List
from ._birther import _Birther
from ...parameters.balances.freight import Freight

if TYPE_CHECKING:
    from ..._core._aliases._is_component import IsLinkage, IsResource
    from ..._core._aliases._is_input import IsBoundInput, IsExactInput, IsBalInput


@dataclass
class Transit(_Birther):
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

    freight: IsBalInput = field(default=None)
    loss: IsExactInput = field(default=None)
    transport: IsBoundInput = field(default=None)
    linkages: List[IsLinkage] = field(default=None)
    ship: IsBoundInput = field(default=None)
    speed: IsExactInput = field(default=None)

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

    @staticmethod
    def _spatials():
        """Spatial Components where the Operation is located"""
        return 'linkages'

    @staticmethod
    def resourcebnds():
        """Attrs that quantify the bounds of the Component"""
        return ['ship']

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
        """Balance attribute"""
        return self.freight

    @property
    def capacity_in(self):
        """Capacity of the Loading Process"""
        return self.capacity

    @property
    def capacity_out(self):
        """Capacity of the Unloading Process"""
        return self.capacity

    def freightize(self):
        """Makes the freight"""
        if not isinstance(self.freight, Freight):
            self.freight = Freight(freight=self.freight, transit=self)
            self._balanced = True
