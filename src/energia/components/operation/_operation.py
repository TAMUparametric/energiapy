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
        self._fab: Conversion = None

    @property
    def fab(self) -> Conversion:
        """Material conversion"""

        if self._fab is None:
            # will be made the first time it is called
            self._fab = Conversion(operation=self)
        return self._fab

    @property
    def base(self) -> Resource:
        """Base resource"""
        return self.conv.base

    @property
    def conversion(self) -> dict[Resource, int | float]:
        """Conversion of commodities"""
        return self.conv.conversion

    @property
    def fabrication(
        self,
    ) -> (
        dict[Resource, int | float | list[int | float]]
        | dict[int | str, dict[Resource, int | float | list[int | float]]]
    ):
        """Material conversion of commodities"""
        return self.fab.conversion


    @property
    def lag(self) -> Lag:
        """Lag of the process"""
        return self.conv.lag
