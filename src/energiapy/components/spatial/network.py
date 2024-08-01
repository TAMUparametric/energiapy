""" energiapy.Network - made up of Locations connected by Linkages
"""
from __future__ import annotations

from typing import TYPE_CHECKING, List

from dataclasses import dataclass, field

from ...core.inits.component import CmpInit

if TYPE_CHECKING:
    from ...types.alias import IsInput, IsLinkage


@dataclass
class Network(CmpInit):
    locations: List[IsInput] = field(default_factory=list)
    linkages: List[IsLinkage] = field(default_factory=list)

    def __post_init__(self):
        CmpInit.__post_init__(self)

    @property
    def collection(self):
        """The collection in scenario
        """
        return 'network'
