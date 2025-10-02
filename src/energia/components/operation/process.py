"""Process"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from warnings import warn

from ...modeling.parameters.conversion import Conversion
from ._operation import _Operation

if TYPE_CHECKING:
    from ..commodity.resource import Resource
    from ..spatial.location import Location
    from ..temporal.lag import Lag
    from ..temporal.periods import Periods
    from .storage import Storage


@dataclass
class Process(_Operation):
    """Process converts one Resource to another Resource
    at some Location

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
    :ivar _indexed: True if an index set has been created.
    :vartype _indexed: bool
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
    :ivar locations: Locations at which the process is balanced. Defaults to [].
    :vartype locations: list[Location]
    :ivar ofstorage: If the Process is Storage charging and discharging. Defaults to None.
    :vartype ofstorage: Storage, optional
    """

    def __post_init__(self):
        _Operation.__post_init__(self)

        # at which locations the process is balanced
        # Note that we do not need a conversion at every temporal scale.
        # once balanced at a location for a particular time,
        # if time != horizon, the individual streams are summed up anyway
        self.locations: list[Location] = []

        self.ofstorage: Storage = None

    @property
    def spaces(self) -> list[Location]:
        """Locations at which the process is balanced"""
        return self.locations

    def locate(self, *locations: Location):
        """Locate the process"""

        # get location, time tuples where operation is defined
        loc_times: list[tuple[Location, Periods]] = []
        for loc in locations:

            if self not in self.model.capacity.bound_spaces:
                self.model.capacity.bound_spaces[self] = {"ub": [], "lb": []}

            if loc not in self.model.capacity.bound_spaces[self]["ub"]:
                # check if operational capacity has been bound
                print(
                    f"--- Assuming  {self} capacity is unbounded in ({loc}, {self.horizon})",
                )
                # this is not a check, this generates a constraint
                _ = self.capacity(loc, self.horizon) == True

            if self not in self.model.operate.bound_spaces:
                self.model.operate.bound_spaces[self] = {"ub": [], "lb": []}

            if loc not in self.model.operate.bound_spaces[self]["ub"]:
                # check if operate has been bound
                # if not just write opr_{pro, loc, horizon} <= capacity_{pro, loc, horizon}
                print(
                    f"--- Assuming operation of {self} is bound by capacity in ({loc}, {self.horizon})",
                )
                if self in self.model.operate.dispositions:

                    _ = (
                        self.operate(
                            loc,
                            min(self.model.operate.dispositions[self][loc]),
                        )
                        <= 1
                    )
                else:
                    _ = self.operate(loc, self.horizon) <= 1

            # check if the process is being operated at the location
            for d in self.model.operate.domains:
                if d.operation == self and d.space == loc:
                    loc_time = (loc, d.time)
                    if loc_time not in loc_times:
                        loc_times.append(loc_time)

        self.writecons_conversion(loc_times)

        if self.fabrication:
            self.writecons_fabrication(loc_times)

    def writecons_conversion(self, loc_times: list[tuple[Location, Periods]]):
        """Write the conversion constraints for the process"""

        def time_checker(res: Resource, loc: Location, time: Periods):
            """This checks if it is actually necessary
            to write conversion at denser temporal scales
            """
            # This checks whether some other aspect is defined at
            # a lower temporal scale

            if loc not in self.model.grb[res]:
                # if not defined for that location, check for a lower order location
                # i.e. location at a lower hierarchy,
                # e.g. say if loc being passed is a city, and a grb has not been defined for it
                # then we need to check at a higher order
                parent = self.space.split(loc)[1]  # get location at one hierarchy above
                if parent:
                    # if that indeed exists, then make the parent the loc
                    # the conversion Balance variables will feature in grb for parent location
                    loc = parent

                self.model.update_grb(resource=res, space=loc, time=time)

            if time not in self.model.grb[res][loc]:
                self.model.update_grb(resource=res, space=loc, time=time)

            if res.inv_of:
                # for inventoried resources, the conversion is written
                # using the time of the base resource's grb
                res = res.inv_of

            try:
                times = list(
                    [
                        t
                        for t in self.model.grb[res][loc]
                        if self.model.grb[res][loc][t]
                    ],
                )
            except KeyError:
                times = []
            # write the conversion balance at
            # densest temporal scale in that space
            if times:
                return min(times)

            return time.horizon

        if not self.conv:
            warn(
                f"{self}: Conversion not defined, no Constraints generated",
                UserWarning,
            )
            return

        # This makes the conversion consistent
        # check conv_test.py in tests for examples
        self.conv.balancer()

        if self.conv.pwl:
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

            conversion = self.conversion[list(self.conversion)[0]]

        else:
            conversion = self.conversion

        for loc_time in loc_times:
            loc = loc_time[0]
            time = loc_time[1]

            if loc in self.locations:
                # if the process is already balanced for the location , Skip

                continue

            for res, par in conversion.items():
                # set, the conversion on the resource

                setattr(res, self.name, self)
                # now there are two cases possible
                # the parameter (par) is positive or negative
                # if positive, the resource is expended
                # if negative, the resource is produced
                # also, the par can be an number or a list of numbers

                # insitu resource (produced and expended within the system)
                # do not initiate a grb so we need to run a check for that first
                if res in self.model.grb:
                    time = time_checker(res, loc, time)
                    if self.model.grb[res][loc][time]:
                        _insitu = False
                    else:
                        _insitu = True
                else:
                    # this implies that the grb needs to be initiated
                    # by declaring relevant variable
                    # the relevant variable will be unbounded
                    _insitu = True

                # upd_expend, upd_produce, upd_operate = False, False, False

                if isinstance(par, (int | float)) and par < 0:
                    # if par == 0:
                    #     continue

                    # if par < 0:
                    # condition: negative number
                    eff = -par
                    if self.lag:
                        opr = self.operate(loc, self.lag.of)
                        rhs = res.expend(self.operate, loc, self.lag.of)
                    else:
                        opr = self.operate(loc, time)
                        rhs = res.expend(self.operate, loc, time)

                elif isinstance(par, list) and par[0] < 0:
                    # NOTE: this only checks the sign of the first element
                    # if par[0] < 0:
                    # condition: list with negative numbers
                    eff = [-i for i in par]

                    if self.lag:
                        opr = self.operate(loc, self.lag.of)
                        rhs = res.expend(self.operate, loc, self.lag.of)
                    else:
                        opr = self.operate(loc, time)
                        rhs = res.expend(self.operate, loc, time)

                    # if par[0] == 0:
                    #     continue

                else:
                    # condition: positive number or list of positive numbers
                    eff = par

                    if self.lag:
                        # Lag is considered on the outset
                        # i.e. commodities are immediately consumed, and produced after lag
                        opr = self.operate(loc, self.lag)
                        rhs = res.produce(self.operate, loc, self.lag.of)
                    else:
                        opr = self.operate(loc, time)
                        rhs = res.produce(self.operate, loc, time)

                if _insitu:
                    # this initiates a grb
                    res.insitu = True
                    _ = rhs(self.operate, loc, time) == True

                # if list, a time match will be done,
                # because of using .balancer(), expend/produce thus on same temporal scale

                if self.conv.pwl:

                    eff = [conv[res] for conv in self.conversion.values()]

                    if eff[0] < 0:
                        eff = [-e for e in eff]

                    if not self.conv.modes_set:
                        # this is setting the bin limits for piece wise linear conversion
                        # these are written bound to capacity generally
                        # but here we pause that binding and bind operate to explicit limits
                        self.model.operate.bound = None

                        _ = opr == {n: k for n, k in enumerate(self.conversion.keys())}

                        # reset capacity binding
                        self.model.operate.bound = self.model.capacity

                        modes = self.model.modes[-1]
                        self.conv.modes_set = True

                    else:
                        modes = self.conv.modes
                        modes.bind = self.operate
                        self.conv.modes_set = True

                    opr = opr(modes)

                    rhs = rhs(modes)

                    # _ = opr(modes)[rhs(modes)] == eff

                # else:
                _ = opr[rhs] == eff

            # update the locations at which the process exists
            self.locations.append(loc)

    def __call__(self, resource: Resource | Conversion, lag: Lag = None) -> Conversion:
        """Conversion is called with a Resource to be converted"""

        if not self._conv:
            self.conv = Conversion(operation=self)
            self._conv = True

        self.conv.lag = lag
        return self.conv(resource)
