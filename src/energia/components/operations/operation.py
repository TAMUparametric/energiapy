"""A General Operation."""

from __future__ import annotations

import logging
from abc import abstractmethod
from collections.abc import Iterator
from functools import cached_property
from typing import TYPE_CHECKING

from ..._core._component import _Component
from ...modeling.parameters.conversion import Conversion
from ...modeling.parameters.conversions import Construction
from ...utils.decorators import timer

logger = logging.getLogger("energia")

if TYPE_CHECKING:
    from gana.sets.constraint import C
    from gana.sets.function import F

    from ...modeling.indices.domain import Domain
    from ...modeling.indices.sample import Sample
    from ...modeling.variables.aspect import Aspect
    from ..commodities.resource import Resource
    from ..spatial.linkage import Linkage
    from ..spatial.location import Location
    from ..temporal.lag import Lag
    from ..temporal.periods import Periods


class Operation(_Component):
    """
    A General Operation.

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
    :vartype conversion: Conversion, optional
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
        """Collect the supplied conversions and initialize the operation's construction balance."""
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
        """Locations at which the process is balanced."""

    @cached_property
    def capacity_aspect(self) -> Aspect:
        """Capacity Aspect."""
        return self.model.capacity

    @cached_property
    def operate_aspect(self) -> Aspect:
        """Operate Aspect."""
        return self.model.operate

    @property
    def operate_sample(self) -> Sample:
        """Operate Sample."""
        return self.operate

    @property
    def capacity_sample(self) -> Sample:
        """Capacity Sample."""
        return self.capacity

    @property
    def basis(self) -> Resource | None:
        """Base resource."""
        if self.primary_conversion is not None:
            return self.primary_conversion.resource
        return None

    @property
    def balance(self) -> dict[Resource, int | float] | None:
        """Conversion of commodities."""
        if self.primary_conversion is not None:
            return self.primary_conversion.balance
        return None

    @property
    def lag(self) -> Lag | None:
        """Lag of the process."""
        if self.primary_conversion is not None:
            return self.primary_conversion.lag
        return None

    def write_primary_conversion(
        self,
        space_times: list[tuple[Location | Linkage, Periods]],
    ):
        """Write conversion constraints for the operation."""

    @timer(logger, kind="construction")
    def write_construction(
        self,
        space_times: list[tuple[Location | Linkage, Periods]],
        # fabrication: dict[Resource, int | float | list[int | float]],
    ):
        """Write fabrication constraints for the operation."""
        self.construction.balancer()

        for location, time in space_times:
            self.construction.write(location, time)

        return self, (spc for spc, _ in space_times)

    @timer(logger, kind="assume-capacity")
    def _check_capacity_bound(self, space: Location | Linkage):
        """Check if capacity is bounded in space."""
        if self not in self.capacity_aspect.bound_spaces:
            # ensure that the bound_spaces dict is initialized
            self.capacity_aspect.bound_spaces[self] = {"ub": [], "lb": []}

        if space not in self.capacity_aspect.bound_spaces[self]["ub"]:
            # check if operational capacity has been bound
            # this is not a check, this generates a constraint
            _ = self.capacity_sample(space, self.horizon) >= 0

            return self, space, self.horizon

        return False

    def _operating_time(self, space: Location | Linkage) -> Periods:
        operations = self.model.dispositions.get(self.operate_aspect, {})
        return min(operations.get(self, {}).get(space, ()), default=self.horizon)

    def _mapped_totals(self, domain: Domain) -> Iterator[Domain]:
        """Yield coarser domains connected by existing time-sum constraints."""
        time_maps = self.operate_aspect.maps["time"]
        for period in domain.periods.coarser_periods:
            total = domain.edit({"periods": period})
            if domain in time_maps.get(total, ()):
                yield total
                yield from self._mapped_totals(total)

    @staticmethod
    def _implies_capacity(bound: C, reference: F) -> bool:
        """Check each aggregate row against activity - capacity <= 0."""
        if len(bound) != len(reference):
            return False
        for row, limit in zip(bound, reference, strict=True):
            # Gana stores parameter columns in Z, the constant RHS in B, and
            # variable columns and their coefficients in P and A, respectively.
            if row.Z or row.B > 0:
                return False
            # A nonpositive cap on activity also implies the capacity bound.
            if row.P == limit.P[:1] and row.A == [1]:
                continue
            if row.P != limit.P or row.A[0] != 1 or row.A[1] < -1:
                return False
        return True

    def _inherits_capacity_bound(self, sample: Sample) -> bool:
        # Operating activity is nonnegative, so every term in a time sum is
        # bounded by its total. Only a bound against the same capacity counts.
        aspect = self.operate_aspect
        for total in self._mapped_totals(sample.domain):
            for relation in ("ub", "eq"):
                name = f"{aspect.name}{total.idxname}_{relation}"
                if name in aspect.constraints:
                    reference = aspect(domain=total).V() - sample.Vb()
                    if self._implies_capacity(getattr(self.program, name), reference):
                        return True
        return False

    @timer(logger, kind="assume-operate")
    def _check_operate_bound(self, space: Location | Linkage, time: Periods):
        aspect = self.operate_aspect
        try:
            bounds = self.model.scenario[aspect][self][space][time]
        except KeyError:
            bounds = {}
        if "ub" in bounds or "eq" in bounds:
            return False

        sample = self.operate_sample(space, time)
        if aspect.nn and self._inherits_capacity_bound(sample):
            return False
        _ = sample <= 1
        return self, space, time

    def _update_space_times(
        self,
        space: Location | Linkage,
        space_times: list[tuple[Location | Linkage, Periods]],
    ):
        """Update space times for the operation."""
        for domain in self.operate_aspect.domains:
            if domain.space == space:
                space_time = (space, domain.time)
                if space_time not in space_times:
                    space_times.append(space_time)

        return space_times

    @timer(logger, kind="locate")
    def locate(self, *spaces: Location | Linkage):
        """Locate the process."""
        if not spaces:
            spaces = (self.model.network,)

        space_times: list[tuple[Location | Linkage, Periods]] = []

        placements = []
        for space in spaces:
            self._check_capacity_bound(space)
            time = self._operating_time(space)
            placements.append((space, time))
            self._check_operate_bound(space, time)

            space_times = self._update_space_times(space, space_times)

        self.write_primary_conversion(space_times)

        if self.construction:
            self.write_construction(self.space_times)

        for space, initial_time in placements:
            time = self._operating_time(space)
            if time is not initial_time:
                self._check_operate_bound(space, time)

        return self, spaces

    def __call__(
        self,
        resource: Resource | Conversion,
        lag: Lag | None = None,
    ) -> Conversion:
        """
        Conversion is called with a Resource to be converted.

        .. admonition:: Example

            .. code-block:: python

                from energia import Model, Periods, Process, Resource

                m = Model()
                m.hour = Periods()
                m.fuel, m.heat = Resource(), Resource()
                m.boiler = Process()
                m.boiler(m.heat, lag=-m.hour) == -m.fuel
                assert m.boiler.lag.of is m.hour
        """
        self.primary_conversion.resource = resource
        if lag:
            return self.primary_conversion(resource, lag)
        return self.primary_conversion(resource)

    def __setattr__(self, name, value):
        """Attach pending conversions to the operation when it joins a model."""
        if name == "model" and value is not None:
            for conv in self.conversions:
                conv.operation = self

            if len(self.conversions) == 1:
                self.primary_conversion.balance.update(self.conversions[0])
                self.primary_conversion.resource = self.conversions[0].resource

        super().__setattr__(name, value)
