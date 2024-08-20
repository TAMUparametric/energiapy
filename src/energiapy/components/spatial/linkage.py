"""Linkage links Locations
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ._spatial import _Spatial

if TYPE_CHECKING:
    from ..._core._aliases._is_component import IsLocation


@dataclass
class Linkage(_Spatial):
    """Linkage between Locations

    If bi is True, the Linkage is bothways and a Linkage_ is birthed

    Attributes:
        sink (IsLocation): Location where the Resource is sent
        source (IsLocation): Location where the Resource is received
        bi (bool): True in direction of the Linkage is bothways
        distance (float): distance between Locations
        label (str): label of the Linkage

    """

    sink: IsLocation = field(default=None)
    source: IsLocation = field(default=None)
    bi: bool = field(default=True)
    distance: float = field(default=None)
    label: str = field(default=None)

    def __post_init__(self):
        _Spatial.__post_init__(self)

    @property
    def transits(self):
        """Storage Operations at the Location"""
        return self.fetch('transits')

    @property
    def operations(self):
        """Operations at the Location"""
        return self.transits
