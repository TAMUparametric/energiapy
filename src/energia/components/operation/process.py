"""Process"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from warnings import warn


from ...modeling.parameters.conversion import Conversion
from ._operation import _Operation
from ..temporal.modes import Modes

if TYPE_CHECKING:
    from ..commodity.resource import Resource
    from ..measure.unit import Unit
    from ..spatial.linkage import Linkage
    from ..spatial.location import Location
    from ..temporal.lag import Lag
    from ..temporal.period import Period
    from .storage import Storage


@dataclass
class Process(_Operation):
    """Process converts one Resource to another Resource
    at some Location"""

    def __post_init__(self):
        _Operation.__post_init__(self)

        # at which locations the process is balanced
        # Note that we do not need a conversion at every temporal scale.
        # once balanced at a location for a particular time,
        # if time != horizon, the individual streams are summed up anyway
        self.locs: list[Location] = []

        self.ofstorage: Storage = None

        # operating mode
        self.mode: Modes = None

    def locate(self, *locs: Location):
        """Locate the process"""

        # get location, time tuples where operation is defined
        loc_times: list[tuple[Location, Period]] = []
        for loc in locs:

            if self not in self.model.capacity.bound_spaces:
                self.model.capacity.bound_spaces[self] = {'ub': [], 'lb': []}

            if loc not in self.model.capacity.bound_spaces[self]['ub']:
                # check if operational capacity has been bound
                print(
                    f'--- Assuming  {self} capacity is unbounded in ({loc}, {self.horizon})'
                )
                # this is not a check, this generates a constraint
                _ = self.capacity(loc, self.horizon) == True

            if self not in self.model.operate.bound_spaces:
                self.model.operate.bound_spaces[self] = {'ub': [], 'lb': []}

            if loc not in self.model.operate.bound_spaces[self]['ub']:
                # check if operate has been bound
                # if not just write opr_{pro, loc, horizon} <= capacity_{pro, loc, horizon}
                print(
                    f'--- Assuming operation of {self} is bound by capacity in ({loc}, {self.horizon})'
                )
                _ = self.operate(loc, self.horizon) <= 1

            # check if the process is being operated at the location
            for d in self.model.operate.domains:
                if d.operation == self and d.space == loc:
                    loc_time = (loc, d.time)
                    if loc_time not in loc_times:
                        loc_times.append(loc_time)

        self.writecons_conversion(loc_times)

    def writecons_conversion(self, loc_times: list[tuple[Location, Period]]):
        """Write the conversion constraints for the process"""
        if not self.conv:
            warn(
                f'{self}: Conversion not defined, no Constraints generated', UserWarning
            )
            return

        self.conv.balancer()

        def time_checker(res: Resource, loc: Location, time: Period):
            """This checks if it is actually necessary
            to write conversion at denser temporal scales
            """
            # This checks whether some other aspect is defined at
            # a lower temporal scale

            if not loc in self.model.grb[res]:
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

            if not time in self.model.grb[res][loc]:
                self.model.update_grb(resource=res, space=loc, time=time)

            if res.inv_of:
                # for inventoried resources, the conversion is written
                # using the time of the base resource's grb
                res = res.inv_of

            times = list(
                [t for t in self.model.grb[res][loc] if self.model.grb[res][loc][t]]
            )
            # write the conversion balance at
            # densest temporal scale in that space
            if times:
                return min(times)

            return time.horizon

        for loc_time in loc_times:
            loc = loc_time[0]
            time = loc_time[1]

            if loc in self.locs:
                # if the process is already balanced for the location , Skip

                continue

            if self.conv.pwl:
                # if piece wise linear conversion is being used
                # TODO - stopped here
                continue

            for res, par in self.conversion.items():
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
                    # condition: negative number
                    eff = -par

                    if self.lag:
                        opr = self.operate(loc, self.lag.of)
                        rhs = res.expend(self.operate, loc, self.lag.of)
                    else:
                        opr = self.operate(loc, time)
                        rhs = res.expend(self.operate, loc, time)

                elif isinstance(par, list) and par[0] < 0:

                    # condition: list with negative numbers
                    eff = [-i for i in par]

                    if self.lag:
                        opr = self.operate(loc, self.lag.of)
                        rhs = res.expend(self.operate, loc, self.lag.of)
                    else:
                        opr = self.operate(loc, time)
                        rhs = res.expend(self.operate, loc, time)

                else:
                    # condition: positive number or list of positive numbers
                    eff = par

                    if self.lag:
                        # Lag is considered on the outset
                        # i.e. commodities are immediately consumed, and produced after lag
                        opr = self.operate(loc, self.lag.of)
                        rhs = res.produce(self.operate, loc, self.lag)
                    else:
                        opr = self.operate(loc, time)
                        rhs = res.produce(self.operate, loc, time)

                if _insitu:
                    # this initiates a grb
                    res.insitu = True
                    _ = rhs(self.operate, loc, time) == True

                # if list, a time match will be done,
                # because of using .balancer(), expend/produce thus on same temporal scale
                _ = opr[rhs] == eff

            # update the locations at which the process exists
            self.locs.append(loc)

    def __call__(self, resource: Resource | Conversion, lag: Lag = None) -> Conversion:
        """Conversion is called with a Resource to be converted"""

        if not self._conv:
            self.conv = Conversion(operation=self)
            self._conv = True

        self.conv.lag = lag
        return self.conv(resource)
