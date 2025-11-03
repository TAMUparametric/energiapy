"""Transport"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from ...modeling.parameters.conversion import Conversion
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

        self.primary_conversion = Conversion(
            operation=self,
            aspect='operate',
            add="ship_in",
            sub="ship_out",
            attr_name="freight",
        )

        self.production = Conversion(
            operation=self,
            aspect='operate',
            add="produce",
            sub="expend",
            attr_name="production",
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

    # @timer(logger, kind="production")
    # def write_primary_conversion(self, space_times: list[tuple[Location, Periods]]):
    #     """Write the production constraints for the process"""

    #     # This makes the production consistent
    #     # check conv_test.py in tests for examples
    #     self.production.balancer()

    # def write_transportation(self, link_times: list[tuple[Linkage, Periods]]):
    #     """Write Transportation constraints for the transport"""
    #     self.transportation.balancer()

    # def write_production(self, link_times: list[tuple[Linkage, Periods]]):
    #     """Write the conversion constraints for the transport"""

    #     def time_checker(res: Resource, loc: Location, time: Periods):
    #         """This checks if it is actually necessary
    #         to write conversion at denser temporal scales
    #         """
    #         # This checks whether some other aspect is defined at
    #         # a lower temporal scale

    #         if loc not in self.model.balances[res]:
    #             # if not defined for that location, check for a lower order location
    #             # i.e. location at a lower hierarchy,
    #             # e.g. say if loc being passed is a city, and a grb has not been defined for it
    #             # then we need to check at a higher order
    #             parent = self.space.split(loc)[1]  # get location at one hierarchy above
    #             if parent:
    #                 # if that indeed exists, then make the parent the loc
    #                 # the conversion Balance variables will feature in grb for parent location
    #                 loc = parent

    #         _ = self.model.balances[res][loc][time]

    #         #     self.model.update_balances(resource=res, space=loc, time=time)

    #         # if time not in self.model.balances[res][loc]:
    #         #     self.model.update_balances(resource=res, space=loc, time=time)
    #         if res.inv_of:
    #             # for inventoried resources, the conversion is written
    #             # using the time of the base resource's grb
    #             res = res.inv_of

    #         times = list(
    #             [
    #                 t
    #                 for t in self.model.balances[res][loc]
    #                 if self.model.balances[res][loc][t]
    #             ],
    #         )
    #         # write the conversion balance at
    #         # densest temporal scale in that space
    #         if times:
    #             return min(times)

    #         return time.horizon

    #     self.production.balancer()

    #     if self.production.pwl:

    #         conversion = self.balance[list(self.balance)[0]]

    #     else:
    #         conversion = self.balance

    #     shipping_conversion, rest_conversion = {self.production.resource: 1}, {
    #         k: v for k, v in conversion.items() if k != self.production.resource
    #     }

    #     for link_time in link_times:
    #         link, time = link_time
    #         source, sink = link.source, link.sink

    #         # time = link_time[1]

    #         if link in self.linkages:
    #             # if the transport is already balanced for the location , Skip
    #             continue

    #         for res, par in conversion.items():
    #             # set, the conversion on the resource
    #             setattr(res, self.name, self)
    #             # now there are two cases possible
    #             # the parameter (par) is positive or negative
    #             # if positive, the resource is expend
    #             # if negative, the resource is produced
    #             # also, the par can be an number or a list of numbers

    #             # insitu resource (expended and ship_outed within the system)
    #             # do not initiate a grb so we need to run a check for that first
    #             if res in self.model.balances:
    #                 time = time_checker(res, link.source, time)

    #                 if self.model.balances[res][link][time]:
    #                     # if the grb has been defined for that resource at that location and time
    #                     _insitu = False
    #                 else:
    #                     _insitu = True
    #             else:
    #                 # this implies that the grb needs to be initiated
    #                 # by declaring relevant variable
    #                 # the relevant variable will be unbounded
    #                 _insitu = True

    #             if isinstance(par, (int | float)) and par < 0:
    #                 # condition: negative number
    #                 eff = -par

    #                 if self.lag:
    #                     opr = self.operate(link, self.lag.of)
    #                     rhs = res.expend(self.operate, link.source, self.lag.of)
    #                 else:
    #                     opr = self.operate(link, time)
    #                     rhs = res.expend(opr, link.source, time)

    #             elif isinstance(par, list) and par[0] < 0:
    #                 # condition: list with negative numbers
    #                 eff = [-i for i in par]

    #                 if self.lag:
    #                     opr = self.operate(link, self.lag.of)
    #                     rhs = res.expend(self.operate, link.source, self.lag.of)
    #                 else:
    #                     opr = self.operate(link, time)
    #                     rhs = res.expend(self.operate, link.source, time)

    #             else:
    #                 # condition: positive number or list of positive numbers
    #                 eff = par

    #                 if self.lag:
    #                     opr = self.operate(link, self.lag)
    #                     rhs_export = self.model.ship_out(
    #                         res,
    #                         self.operate,
    #                         link.source,
    #                         self.lag.of,
    #                     )
    #                     rhs_import = self.model.ship_in(
    #                         res,
    #                         self.operate,
    #                         link.sink,
    #                         self.lag,
    #                     )
    #                 else:
    #                     opr = self.operate(link, time)
    #                     rhs_export = self.model.ship_out(
    #                         res,
    #                         self,
    #                         link.source,
    #                         time_checker(res, link.source, time),
    #                     )
    #                     rhs_import = self.model.ship_in(
    #                         res,
    #                         self,
    #                         link.sink,
    #                         time_checker(res, link.sink, time),
    #                     )

    #             if _insitu:
    #                 res.insitu = True
    #                 _ = rhs_export == True
    #                 _ = rhs_import == True

    #             if self.production.pwl:

    #                 eff = [conv[res] for conv in self.balance.values()]

    #                 if eff[0] < 0:
    #                     eff = [-i for i in eff]

    #                 if not self.production.modes_set:
    #                     self.model.operate.bound = None
    #                     _ = opr == dict(enumerate(self.balance.keys()))

    #                     self.model.operate.bound = self.production.model.capacity

    #                     modes = self.model.modes[-1]
    #                     self.production.modes_set = True

    #                 else:
    #                     modes = self.production.modes
    #                     modes.bind = self.operate
    #                     self.production.modes_set = True

    #                 opr = opr(modes)
    #                 rhs_export = rhs_export(modes)
    #                 rhs_import = rhs_import(modes)

    #             _ = opr[rhs_export] == eff
    #             _ = opr[rhs_import] == eff

    #             self.linkages.append(link)
