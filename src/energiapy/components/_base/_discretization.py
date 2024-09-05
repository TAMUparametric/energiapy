"""A discretization of the scope 
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from ._component import _Component


if TYPE_CHECKING:
    from ..temporal.scale import Scale
    from ..spatial.location import Location
    from ..temporal.horizon import Horizon
    from ..spatial.network import Network


@dataclass
class _Discr(_Component):
    """A discretization of the scope
    - Scales for Horizon
    - Locations for Network
    """

    parent: Scale | Location | Horizon | Network = field(default=None)

    def __post_init__(self):
        _Component.__post_init__(self)
        self.child = None
        self.parent.child = self

    @property
    def index(self):
        """Index of the Discretization"""
        return self.parent.index + (self,)
