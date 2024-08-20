"""Transit moves Resources between Locations
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List

from ._operational import _Operational

if TYPE_CHECKING:
    from ..._core._aliases._is_component import IsLinkage, IsResource
    from ..._core._aliases._is_input import IsBoundInput, IsExactInput


@dataclass
class Transit(_Operational):
    """Transit moves Resources between Locations through a Linkage

    Attributes:
        capacity (IsBoundInput): bound on the capacity of the Operation
        land (IsExactInput): land use per Capacity
        material (IsExactInput): material use per Capacity
        capex (IsExactInput): capital expense per Capacity
        opex (IsExactInput): operational expense based on Operation
        emission (IsExactInput): emission due to construction per Capacity
        loss: (IsExactInput): loss of resource during transportation
        carries (IsResource): Resource carried by the Operation
        transport (IsBoundInput): bound by Capacity. Reported by operate as well.
        linkages (List[IsLinkage]): linkages between which Transit exists
        basis (str): basis of the component
        citation (dict): citation of the component
        block (str): block of the component
        introduce (str): index in scale when the component is introduced
        retire (str): index in scale when the component is retired
        label (str): label of the component

    """

    carries: IsResource = field(default=None)
    loss: IsExactInput = field(default=None)
    transport: IsBoundInput = field(default=None)
    linkages: List[IsLinkage] = field(default=None)

    def __post_init__(self):
        _Operational.__post_init__(self)

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
        return ['ship', 'deliver']

    @staticmethod
    def resourceexps():
        """Attrs that determine resource expenses of the component"""
        return []

    @staticmethod
    def resourceloss():
        """Attrs that determine resource loss of the component"""
        return ['loss']

    @property
    def resources(self):
        """Resources in Inventory"""
        return [self.carries]
