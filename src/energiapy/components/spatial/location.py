""" energiapy.Location
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ...core.inits.component import CmpInit

if TYPE_CHECKING:
    from ...types.alias import IsInput


@dataclass
class Location(CmpInit):
    """Location where Process and Storage can reside 
    """
    land_cost: IsInput = field(default=None)
    land_avail: IsInput = field(default=None)

    def __post_init__(self):
        CmpInit.__post_init__(self)

    @property
    def _spatial(self):
        return self

    @property
    def collection(self):
        """The collection in scenario
        """
        return 'locations'
