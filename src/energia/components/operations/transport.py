"""Transport"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from ...modeling.parameters.conversions import Production, Transportation
from ...utils.decorators import timer
from .operation import Operation

logger = logging.getLogger("energia")

if TYPE_CHECKING:
    # from ..commodities.resource import Resource
    from ..spatial.linkage import Linkage
    from ..spatial.location import Location
    from ..temporal.periods import Periods


class Transport(Operation):
    """
    Exports Resource through Link basically, moves Resources between Locations

    :param basis: Unit basis of the component. Defaults to None.
    :type basis: Unit, optional
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
    :ivar linkages: List of Linkages where the transport is located. Defaults to [].
    :vartype linkages: list[Linkage]
    """

    def __init__(self, *args, label: str = "", citations: str = "", **kwargs):

        Operation.__init__(self, *args, label=label, citations=citations, **kwargs)
        self.linkages: list[Linkage] = []

        self.primary_conversion = Transportation(
            operation=self,
        )

        self.production = Production(
            operation=self,
        )

    @property
    def transportation(self):
        """Alias for primary_conversion"""
        return self.primary_conversion

    @transportation.setter
    def transportation(self, value):
        """Set primary_conversion"""
        self.primary_conversion = value

    @property
    def spaces(self) -> list[Linkage]:
        """Locations at which the process is balanced"""
        return self.linkages

    def _set_transportation_balance(self):
        """Get the transportation balance from the primary conversion"""

        self.transportation = Transportation.from_balance(
            balance={self.basis: self.primary_conversion.balance[self.basis]},
            **self.primary_conversion.args,
        )

        self.transportation.balancer()

    def _set_production_balance(self):
        """Get the production balance from the primary conversion"""

        self.production = Production.from_balance(
            balance={
                k: v
                for k, v in self.primary_conversion.balance.items()
                if k != self.basis
            },
            **self.primary_conversion.args,
        )

        self.production.balancer()

    @timer(logger, kind="production")
    def write_primary_conversion(self, space_times: list[tuple[Location, Periods]]):
        """Write the production constraints for the process"""

        if len(self.primary_conversion) > 1:
            # this means that there are other dependent conversions
            # besides transport such as production and expending of other resources

            self._set_transportation_balance()

            self._set_production_balance()

            _write_production = True
        else:
            _write_production = False

        for space, time in space_times:

            if space in self.spaces:
                # if the process is already balanced for the space , Skip
                continue

            self.transportation.write(space, time)

            if _write_production:
                self.production.write(space, time)

            # update the locations at which the process exists
            self.spaces.append(space)
            self.space_times.append((space, time))

        return self, self.spaces
