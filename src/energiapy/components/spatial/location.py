""" energiapy.Location
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .._component import _Component

if TYPE_CHECKING:
    from ...types.alias import IsInput


@dataclass
class Location(_Component):
    """Location where Process and Storage can reside"""

    land_cost: IsInput = field(default=None)
    land_avail: IsInput = field(default=None)

    def __post_init__(self):
        _Component.__post_init__(self)
        self.processes, self.storages, self.resources = [], [], []

    @property
    def _spatial(self):
        return self

    @property
    def collection(self):
        """The collection in scenario"""
        return 'locations'
