"""A General Operation"""

from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ...core.component import Component
from ...modeling.parameters.conversion import Conversion
from ...modeling.variables.default import Design, Scheduling

if TYPE_CHECKING:
    from ..commodity.resource import Resource
    from ..measure.unit import Unit
    from ..spatial.linkage import Linkage
    from ..spatial.location import Location
    from ..temporal.lag import Lag
    from ..temporal.period import Period


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

        # to check if fab is balanced
        self._fab_balanced: bool = False

    @property
    @abstractmethod
    def spaces(self) -> list[Location | Linkage]:
        """Locations at which the process is balanced"""

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

    def writecons_fabrication(
        self,
        space_times: list[tuple[Location | Linkage, Period]],
        # fabrication: dict[Resource, int | float | list[int | float]],
    ):
        """write fabrication constraints for the operation"""
        if not self._fab_balanced:
            self.fab.balancer()
            self._fab_balanced = True

        for space_time in space_times:
            space = space_time[0]
            time = space_time[1]

            if space in self.spaces:
                continue

        def time_checker():
            # write use on the sparsest temporal index
            return min(self.model.dispositions[self.model.capacity][self][space])

        for res, par in self.fabrication.items():

            if isinstance(par, (int | float)):
                if par == 0:
                    continue

            if isinstance(par, list):
                if par[0] == 0:
                    continue

            if res in self.model.grb:
                time = time_checker()

                if self.model.grb[res][space][time]:
                    _insitu = False
                else:
                    _insitu = True

            else:
                _insitu = True

            if _insitu:
                res.insitu = True
                _ = res.use(self.capacity, space, time) == True

            _ = self.capacity(space, time)[res.use] == par
