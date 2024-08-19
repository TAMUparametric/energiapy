""" energiapy.Linkage links Locations
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ._spatial import _Spatial

if TYPE_CHECKING:
    from ..._core._aliases._is_component import IsLocation


@dataclass
class Linkage(_Spatial):

    sink: IsLocation = field(default=None)
    source: IsLocation = field(default=None)
    bi: bool = field(default=True)
    distance: float = field(default=None)
    label: str = field(default=None)

    def __post_init__(self):
        _Spatial.__post_init__(self)

    # TODO - Block 6

    @property
    def transits(self):
        """Storage Operations at the Location"""
        return self.fetch('transits')

    @property
    def operations(self):
        """Operations at the Location"""
        return self.transits
