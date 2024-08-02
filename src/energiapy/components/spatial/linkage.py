""" energiapy.Linkage links Locations
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ...core.inits.component import CmpInit

if TYPE_CHECKING:
    from ...types.alias import IsInput, IsLocation


@dataclass
class Linkage(CmpInit):
    land_cost: IsInput = field(default=None)
    land_avail: IsInput = field(default=None)
    sink: IsLocation = field(default=None)
    source: IsLocation = field(default=None)
    bi: bool = field(default=False)

    def __post_init__(self):
        CmpInit.__post_init__(self)

    @property
    def collection(self):
        """The collection in scenario
        """
        return 'linkages'
