""" energiapy.Linkage links Locations
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .._component import _Component

if TYPE_CHECKING:
    from ...types.alias import IsInput, IsLocation


@dataclass
class Linkage(_Component):
    land_cost: IsInput = field(default=None)
    land_avail: IsInput = field(default=None)
    sink: IsLocation = field(default=None)
    source: IsLocation = field(default=None)
    bi: bool = field(default=False)

    def __post_init__(self):
        _Component.__post_init__(self)

    @property
    def _spatial(self):
        return self

    @property
    def collection(self):
        """The collection in scenario
        """
        return 'linkages'
