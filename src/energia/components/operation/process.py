"""Process"""

from __future__ import annotations

from typing import TYPE_CHECKING
from warnings import warn

from .operation import Operation

if TYPE_CHECKING:
    from ..commodities.resource import Resource
    from ..spatial.location import Location
    from ..temporal.periods import Periods
    from .storage import Storage


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

        # at which locations the process is balanced
        # Note that we do not need a conversion at every temporal scale.
        # once balanced at a location for a particular time,
        # if time != horizon, the individual streams are summed up anyway
        self.locations: list[Location] = []

    @property
    def spaces(self) -> list[Location]:
        """Locations at which the process is balanced"""
        return self.locations

    def writecons_conversion(self, loc_times: list[tuple[Location, Periods]]):
        """Write the conversion constraints for the process"""

        # def time_checker(res: Resource, loc: Location, time: Periods):
        #     """This checks if it is actually necessary
        #     to write conversion at denser temporal scales
        #     """
        #     # This checks whether some other aspect is defined at
        #     # a lower temporal scale

        #     if loc not in self.model.balances[res]:
        #         # if not defined for that location, check for a lower order location
        #         # i.e. location at a lower hierarchy,
        #         # e.g. say if loc being passed is a city, and a grb has not been defined for it
        #         # then we need to check at a higher order
        #         parent = self.space.split(loc)[1]  # get location at one hierarchy above
        #         if parent:
        #             # if that indeed exists, then make the parent the loc
        #             # the conversion Balance variables will feature in grb for parent location
        #             loc = parent

        #     _ = self.model.balances[res][loc][time]

        #     if res.inv_of:
        #         # for inventoried resources, the conversion is written
        #         # using the time of the base resource's grb
        #         res = res.inv_of

        #     try:
        #         times = list(
        #             [
        #                 t
        #                 for t in self.model.balances[res][loc]
        #                 if self.model.balances[res][loc][t]
        #             ],
        #         )
        #     except KeyError:
        #         times = []
        #     # write the conversion balance at
        #     # densest temporal scale in that space
        #     if times:
        #         return min(times)

        #     return time.horizon

        if not self.production:
            warn(
                f"{self}: Conversion not defined, no Constraints generated",
                UserWarning,
            )
            return

        # This makes the conversion consistent
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

        for location, time in loc_times:

            if location in self.locations:
                # if the process is already balanced for the location , Skip
                continue

            self.production.write(location, time)

            # for res, par in self.production.items():
            #     # set, the conversion on the resource

            #     #! Repurpose
            #     # setattr(res, self.name, self)

            #     # now there are two cases possible
            #     # the parameter (par) is positive or negative
            #     # if positive, the resource is expended
            #     # if negative, the resource is produced
            #     # also, the par can be an number or a list of numbers

            #     # insitu resource (produced and expended within the system)
            #     # do not initiate a grb so we need to run a check for that first

            #     if res in self.model.balances:
            #         time = time_checker(res, location, time)
            #         _ = self.model.balances[res].get(location, {})

            #     eff = par if isinstance(par, list) else [par]

            #     if eff[0] < 0:
            #         # Resources are consumed (expendend by Process) immediately
            #         rhs = res.expend(self.operate, location, time)
            #         eff = [-e for e in eff]
            #     else:
            #         # Production — may occur after lag
            #         lag_time = self.lag.of if self.lag else time
            #         rhs = res.produce(self.operate, location, lag_time)

            #     opr = self.operate(location, time)

            #! PWL
            # because of using .balancer(), expend/produce are on same temporal scale

            # if self.conversion.pwl:

            #     eff = [conv[res] for conv in self.balance.values()]

            #     if eff[0] < 0:
            #         eff = [-e for e in eff]

            #     if not self.conversion.modes_set:
            #         # this is setting the bin limits for piece wise linear conversion
            #         # these are written bound to capacity generally
            #         # but here we pause that binding and bind operate to explicit limits
            #         self.model.operate.bound = None

            #         _ = opr == dict(enumerate(self.balance.keys()))

            #         # reset capacity binding
            #         self.model.operate.bound = self.model.capacity

            #         modes = self.model.modes[-1]
            #         self.conversion.modes_set = True

            #     else:
            #         modes = self.conversion.modes
            #         modes.bind = self.operate
            #         self.conversion.modes_set = True

            #     opr = opr(modes)

            #     rhs = rhs(modes)

            # _ = opr(modes)[rhs(modes)] == eff

            # else:
            # _ = opr[rhs] == eff

            # update the locations at which the process exists
            self.locations.append(location)
