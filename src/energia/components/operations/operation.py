"""A General Operation"""

from __future__ import annotations

import logging
from abc import abstractmethod
from functools import cached_property
from typing import TYPE_CHECKING

from ..._core._component import _Component
from ...modeling.parameters.conversion import Conversion
from ...modeling.parameters.conversions import Construction
from ...utils.decorators import timer

logger = logging.getLogger("energia")

if TYPE_CHECKING:
    from ...modeling.indices.sample import Sample
    from ...modeling.variables.aspect import Aspect
    from ..commodities.resource import Resource
    from ..spatial.linkage import Linkage
    from ..spatial.location import Location
    from ..temporal.lag import Lag
    from ..temporal.periods import Periods


class Operation(_Component):
    """A General Operation

    :param label: An optional label for the component. Defaults to None.
    :type label: str, optional
    :param citations: An optional citation or description for the component. Defaults to None.
    :type citations: str | list[str] | dict[str, str | list[str]], optional

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
    :ivar conversion: Operational conversion associated with the operation. Defaults to None.
    :vartype conversion : Conversion, optional
    :ivar fab: Material conversion associated with the operation. Defaults to None.
    :vartype fab: Conversion, optional
    :ivar _fab_balanced: True if the material conversion has been balanced. Defaults to False.
    :vartype _fab_balanced: bool

    """

    def __init__(
        self,
        *args,
        # operaing_aspect: str,
        label: str = "",
        citations: str = "",
        **kwargs,
    ):
        _Component.__init__(self, label=label, citations=citations, **kwargs)

        self.primary_conversion: Conversion | None = None

        self.construction = Construction(
            operation=self,
            use_max_time=True,
        )

        self.conversions = args
        self.space_times: list[tuple[Location | Linkage, Periods]] = []

    @property
    @abstractmethod
    def spaces(self) -> list[Location | Linkage]:
        """Locations at which the process is balanced"""

    @cached_property
    def capacity_aspect(self) -> Aspect:
        """Capacity Aspect"""
        return getattr(self.model, 'capacity')

    @cached_property
    def operate_aspect(self) -> Aspect:
        """Operate Aspect"""
        return getattr(self.model, 'operate')

    @property
    def operate_sample(self) -> Sample:
        """Operate Sample"""
        return getattr(self, 'operate')

    @property
    def capacity_sample(self) -> Sample:
        """Capacity Sample"""
        return getattr(self, 'capacity')

    @property
    def basis(self) -> Resource:
        """Base resource"""
        if self.primary_conversion is not None:
            return self.primary_conversion.resource

    @property
    def balance(self) -> dict[Resource, int | float]:
        """Conversion of commodities"""
        if self.primary_conversion is not None:
            return self.primary_conversion.balance

    @property
    def lag(self) -> Lag:
        """Lag of the process"""
        if self.primary_conversion is not None:
            return self.primary_conversion.lag

    def write_primary_conversion(
        self,
        space_times: list[tuple[Location | Linkage, Periods]],
    ):
        """write conversion constraints for the operation"""

    @timer(logger, kind="construction")
    def write_construction(
        self,
        space_times: list[tuple[Location | Linkage, Periods]],
        # fabrication: dict[Resource, int | float | list[int | float]],
    ):
        """write fabrication constraints for the operation"""

        self.construction.balancer()

        for location, time in space_times:
            self.construction.write(location, time)

        return self, (spc for spc, _ in space_times)

    @timer(logger, kind='assume-capacity')
    def _check_capacity_bound(self, space: Location | Linkage):
        """Check if capacity is bounded in space"""

        if self not in self.capacity_aspect.bound_spaces:
            # ensure that the bound_spaces dict is initialized
            self.capacity_aspect.bound_spaces[self] = {"ub": [], "lb": []}

        if space not in self.capacity_aspect.bound_spaces[self]["ub"]:
            # check if operational capacity has been bound
            # this is not a check, this generates a constraint
            _ = self.capacity_sample(space, self.horizon) >= 0

            return self, space, self.horizon

        return False

    @timer(logger, kind='assume-operate')
    def _check_operate_bound(self, space: Location | Linkage):
        """Check if operate is bounded in space"""
        if self not in self.operate_aspect.bound_spaces:
            # ensure that the bound_spaces dict is initialized
            self.operate_aspect.bound_spaces[self] = {"ub": [], "lb": []}

        if space not in self.operate_aspect.bound_spaces[self]["ub"]:
            # check if operate has been bound
            # if not just write opr_{pro, space, horizon} <= capacity_{pro, space, horizon}

            if (
                self in self.operate_aspect.dispositions
                and space in self.operate_aspect.dispositions[self]
            ):
                time = min(self.operate_aspect.dispositions[self][space])
            else:
                time = self.horizon
            _ = self.operate_sample(space, time) <= 1

            return self, space, time

        return False

    def _update_space_times(
        self,
        space: Location | Linkage,
        space_times: list[tuple[Location | Linkage, Periods]],
    ):
        """Update space times for the operation"""

        for domain in self.operate_aspect.domains:
            if domain.space == space:
                space_time = (space, domain.time)
                if space_time not in space_times:
                    space_times.append(space_time)

        return space_times

    @timer(logger, kind='locate')
    def locate(self, *spaces: Location | Linkage):
        """Locate the process"""

        if not spaces:
            spaces = (self.model.network,)

        space_times: list[tuple[Location | Linkage, Periods]] = []

        # get location, time tuples where operation is defined
        for space in spaces:

            self._check_capacity_bound(space)

            self._check_operate_bound(space)

            space_times = self._update_space_times(space, space_times)

        self.write_primary_conversion(space_times)

        if self.construction:
            self.write_construction(self.space_times)

        return self, spaces

    def __call__(
        self, resource: Resource | Conversion, lag: Lag | None = None
    ) -> Conversion:
        """Conversion is called with a Resource to be converted"""
        self.primary_conversion.resource = resource
        if lag:
            return self.primary_conversion(resource, lag)
        return self.primary_conversion(resource)

    def __setattr__(self, name, value):

        if name == "model" and value is not None:
            for conv in self.conversions:
                conv.operation = self

            if len(self.conversions) == 1:
                self.primary_conversion += self.conversions[0]
                self.primary_conversion.resource = self.conversions[0].resource

        super().__setattr__(name, value)
