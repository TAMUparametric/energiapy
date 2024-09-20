"""Linkage links Locations through Transits
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ._spatial import _Spatial

if TYPE_CHECKING:
    from .location import Location


@dataclass
class Linkage(_Spatial):
    """Linkage between Locations

    If bi is True, the Linkage is bothways and a Linkage_ is birthed
    bi is then set to False

    Attributes:
        sink (IsLocation): Location where the Resource is sent
        source (IsLocation): Location where the Resource is received
        bi (bool): True in direction of the Linkage is bothways
        distance (float): distance between Locations
        label (str): label of the Linkage

    """

    sink: Location = field(default=None)
    source: Location = field(default=None)
    bi: bool = field(default=True)
    distance: float = field(default=None)
    label: str = field(default=None)

    def __post_init__(self):
        _Spatial.__post_init__(self)
        self._sib = None

    @property
    def transits(self):
        """Storage Operations at the Location"""
        return self.fetch('transits')

    @property
    def operations(self):
        """Operations at the Location"""
        return self.transits

    @property
    def sib(self):
        """Sibling Linkage"""
        return self._sib

    @sib.setter
    def sib(self, linkage):
        self._sib = linkage
