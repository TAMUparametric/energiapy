"""A General Operation"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ...core.component import Component
from ...modeling.parameters.conversion import Conversion
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

        # Operational conversion
        self.conv: Conversion = None

        # Material conversion
        self._make: Conversion = None

    @property
    def make(self) -> Conversion:
        """Material conversion"""

        if self._make is None:
            # will be made the first time it is called
            self._make = Conversion(operation=self)
        return self._make

    @property
    def base(self) -> Resource:
        """Base resource"""
        return self.conv.base

    @property
    def conversion(self) -> dict[Resource, int | float]:
        """Conversion of commodities"""
        return self.conv.conversion

    @property
    def conversion_material(
        self,
    ) -> (
        dict[Resource, int | float | list[int | float]]
        | dict[int | str, dict[Resource, int | float | list[int | float]]]
    ):
        """Material conversion of commodities"""
        return self.make.conversion

    @property
    def lag(self) -> Lag:
        """Lag of the process"""
        return self.conv.lag
