"""A General Operation"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ...core.component import Component
from ...modeling.parameters.conversion import Conv
from ...modeling.variables.default import Design, Scheduling

if TYPE_CHECKING:
    from ..commodity.resource import Resource
    from ..measure.unit import Unit
    from ..spatial.location import Location
    from ..temporal.lag import Lag


@dataclass
class _Operation(Component, Design, Scheduling):
    """A General Operation"""

    def __post_init__(self):
        Component.__post_init__(self)
        self._conv = False
        self.conv: Conv = None

    @property
    def base(self) -> Resource:
        """Base resource"""
        return self.conv.base

    @property
    def conversion(self) -> dict[Resource : int | float]:
        """Conversion of commodities"""
        return self.conv.conversion

    @property
    def lag(self) -> Lag:
        """Lag of the process"""
        return self.conv.lag
