"""Process"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from ...modeling.parameters.conversion import Conversion
from ...modeling.parameters.conversions import Production
from ...utils.decorators import timer
from .operation import Operation

logger = logging.getLogger("energia")

if TYPE_CHECKING:
    from ..spatial.location import Location
    from ..temporal.periods import Periods


class Process(Operation):
    """
    Process converts one Resource to another Resource at some Location

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
    :ivar _conv: True if the operational conversion has been set. Defaults to False.
    :vartype _conv: bool
    :ivar fab: Material conversion associated with the operation. Defaults to None.
    :vartype fab: Conversion, optional
    :ivar _fab_balanced: True if the material conversion has been balanced. Defaults to False.
    :vartype _fab_balanced: bool
    :ivar locations: Locations at which the process is balanced. Defaults to [].
    :vartype locations: list[Location]
    :ivar charges: If the Process is Storage charging. Defaults to None.
    :vartype charges: Storage, optional
    :ivar discharges: If the Process is Storage discharging. Defaults to None.
    :vartype discharges: Storage, optional
    """

    def __init__(self, *args, label: str = "", citations: str = "", **kwargs):

        Operation.__init__(self, *args, label=label, citations=citations, **kwargs)

        self.primary_conversion = Production(
            operation=self,
        )

        # at which locations the process is balanced
        # Note that we do not need a conversion at every temporal scale.
        # once balanced at a location for a particular time,
        # if time != horizon, the individual streams are summed up anyway
        self.locations: list[Location] = []

    @property
    def spaces(self) -> list[Location]:
        """Locations at which the process is balanced"""
        return self.locations

    @property
    def production(self):
        """Alias for primary_conversion"""
        return self.primary_conversion

    @production.setter
    def production(self, value):
        """Set primary_conversion"""
        self.primary_conversion = value

    @timer(logger, kind="production")
    def write_primary_conversion(self, space_times: list[tuple[Location, Periods]]):
        """Write the production constraints for the process"""

        # This makes the production consistent
        # check conv_test.py in tests for examples
        self.production.balancer()

        #! PWL
        # if self.conversion.pwl:
        # if there are piece-wise linear conversions
        # here we assume that the same resources appear in all piece-wise segments
        # this is a reasonable assumption for conversion in processes
        # but not if process modes involve different resources

        # TODO:
        # make the statement eff = [conv[res] for conv in self.conversion.values()]
        # into try
        # if that fails, create a consistent dict, see:
        # {0: {r1: 10, r2: -5}, 1: {r1: 8, r2: -4, r3: -2}}
        # transforms to {0: {r1: 10, r2: -5, r3: 0}, 1: {r1: 8, r2: -4, r3: -2}}
        # the r3: 0 will ensure that r3 is considered in all modes
        # the zero checks will prevent unnecessary constraints
        # there is a problem though, because I am only checking for the elements in the first dict
        # in the multi conversion dict

        #     conversion = self.balance[list(self.balance)[0]]

        # else:

        for space, time in space_times:

            if space in self.locations:
                # if the process is already balanced for the space , Skip
                continue

            self.primary_conversion.write(space, time)

            # update the locations at which the process exists
            self.locations.append(space)
            self.space_times.append((space, time))

        return self, self.locations
