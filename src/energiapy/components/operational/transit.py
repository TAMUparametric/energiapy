"""energiapy.Transit - moves Resources between Locations
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

    carries: IsResource = field(default=None)
    loss: IsExactInput = field(default=None)
    transport: IsBoundInput = field(default=None)
    linkages: List[IsLinkage] = field(default=None)

    def __post_init__(self):
        _Operational.__post_init__(self)

    @property
    def _operate(self):
        """Returns attribute value that signifies operating bounds"""
        return self.transport

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
