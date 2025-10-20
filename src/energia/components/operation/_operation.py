"""A General Operation"""

from __future__ import annotations

import logging
from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..._core._component import _Component
from ...modeling.parameters.conversion import Conversion

logger = logging.getLogger("energia")

if TYPE_CHECKING:
    from ...modeling.constraints.calculate import Calculate
    from ..commodity.resource import Resource
    from ..measure.unit import Unit
    from ..spatial.linkage import Linkage
    from ..spatial.location import Location
    from ..temporal.lag import Lag
    from ..temporal.periods import Periods


class _Operation(_Component):
    """A General Operation

    :param basis: Unit basis of the component. Defaults to None.
    :type basis: Unit, optional
    :param label: An optional label for the component. Defaults to None.
    :type label: str, optional
    :param captions: An optional citation or description for the component. Defaults to None.
    :type captions: str | list[str] | dict[str, str | list[str]], optional

    :ivar model: The model to which the component belongs.
    :vartype model: Model
    :ivar name: Set when the component is assigned as a Model attribute.
    :vartype name: str

    :ivar constraints: List of constraints associated with the component.
    :vartype constraints: list[str]
    :ivar domains: List of domains associated with the component.
    :vartype domains: list[Domain]
    :ivar aspects: Aspects associated with the component with domains.
    :vartype aspects: dict[Aspect, list[Domain]]
    :ivar conv: Operational conversion associated with the operation. Defaults to None.
    :vartype conv: Conversion, optional
    :ivar _conv: True if the operational conversion has been set. Defaults to False.
    :vartype _conv: bool
    :ivar fab: Material conversion associated with the operation. Defaults to None.
    :vartype fab: Conversion, optional
    :ivar _fab_balanced: True if the material conversion has been balanced. Defaults to False.
    :vartype _fab_balanced: bool
    """

    def __init__(self, basis: Unit | None = None, label: str = "", captions: str = ""):

        _Component.__init__(self, basis=basis, label=label, captions=captions)

        self._conv = False

        # Operational conversion
        self.conv: Conversion | None = None

        # Material conversion
        self._fab: Conversion | None = None

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
            self._fab = Conversion(operation=self, bind=self.capacity)
        return self._fab

    @property
    def capex(self) -> Calculate:
        """Capital Expenditure"""
        return self.capacity[self.model.default_currency().spend]

    @property
    def opex(self) -> Calculate:
        """Operational Expenditure"""
        return self.operate[self.model.default_currency().spend]

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
        if self.fab.pwl:
            return {
                mode: self.fab.conversion[_mode]
                for mode, _mode in zip(self.fab.modes, list(self.fab.conversion))
            }

        return self.fab.conversion

    @property
    def lag(self) -> Lag:
        """Lag of the process"""
        return self.conv.lag

    def writecons_fabrication(
        self,
        space_times: list[tuple[Location | Linkage, Periods]],
        # fabrication: dict[Resource, int | float | list[int | float]],
    ):
        """write fabrication constraints for the operation"""
        if not self._fab_balanced:
            self.fab.balancer()
            self._fab_balanced = True

        if self.fab.pwl:
            # n_modes = len(self.fabrication)
            # modes_name = f'bin{len(self.model.modes)}'

            # setattr(self.model, modes_name, Modes(n_modes=n_modes, bind=self.capacity))

            # modes = self.model.modes[-1]

            # this will create modes if not already created
            modes = self.fab.modes

        for space_time in space_times:
            space = space_time[0]
            time = space_time[1]

            if space in self.spaces:
                continue

        def time_checker():
            # write use on the densest temporal index
            return max(self.model.dispositions[self.model.capacity][self][space])

        if self.fab.pwl:

            _modes = list(self.fabrication)
            for n, mode in enumerate(modes):

                for res, par in self.fabrication[_modes[n]].items():

                    if isinstance(par, (int | float)):
                        if par == 0:
                            continue

                    if isinstance(par, list):
                        if par[0] == 0:
                            continue

                    _ = self.capacity(space, time_checker(), mode)[res.use(mode)] == par

        else:

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

    def locate(self, *spaces: Location | Linkage):
        """Locate the process"""

        # get location, time tuples where operation is defined
        space_times: list[tuple[Location | Linkage, Periods]] = []
        for space in spaces:

            if self not in self.model.capacity.bound_spaces:
                self.model.capacity.bound_spaces[self] = {"ub": [], "lb": []}

            if space not in self.model.capacity.bound_spaces[self]["ub"]:
                # check if operational capacity has been bound
                logger.info(
                    f"Assuming  {self} capacity is unbounded in ({space}, {self.horizon})",
                )
                # this is not a check, this generates a constraint
                _ = self.capacity(space, self.horizon) == True

            if self not in self.model.operate.bound_spaces:
                self.model.operate.bound_spaces[self] = {"ub": [], "lb": []}

            if space not in self.model.operate.bound_spaces[self]["ub"]:
                # check if operate has been bound
                # if not just write opr_{pro, space, horizon} <= capacity_{pro, space, horizon}
                logger.info(
                    f"Assuming operation of {self} is bound by capacity in ({space}, {self.horizon})",
                )
                if (
                    self in self.model.operate.dispositions
                    and space in self.model.operate.dispositions[self]
                ):

                    _ = (
                        self.operate(
                            space,
                            min(self.model.operate.dispositions[self][space]),
                        )
                        <= 1
                    )
                else:
                    _ = self.operate(space, self.horizon) <= 1

            # check if the process is being operated at the location
            for d in self.model.operate.domains:
                if d.operation == self and d.space == space:
                    space_time = (space, d.time)
                    if space_time not in space_times:
                        space_times.append(space_time)

        self.writecons_conversion(space_times)

        if self.fabrication:
            self.writecons_fabrication(space_times)

