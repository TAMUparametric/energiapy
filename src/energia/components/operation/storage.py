"""Storage - Stashes Resource to Withdraw Later"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ...core.component import Component
from ...modeling.parameters.conversion import Conv
from ...modeling.variables.default import Capacitate, InvCapacity, Operate, Ramp, Stock
from ..commodity.resource import Resource
from .process import Process

if TYPE_CHECKING:
    from ..spatial.location import Loc
    from ..temporal.period import Period
    from ...modeling.constraints.bind import Bind


@dataclass
class Storage(Component, Stock, InvCapacity, Capacitate, Ramp):  # , Stock):
    """Storage"""

    store: Resource = None

    def __post_init__(self):
        Component.__post_init__(self)
        self.stored = None
        self._conv = False
        self.conv = None
        self.charge = Process()
        self.charge.ofstorage = self
        self.discharge = Process()
        self.discharge.ofstorage = self
        self.locs: list[Loc] = []

    def __setattr__(self, name, value):
        if name == 'model' and value:
            setattr(value, f'{self.name}.charge', self.charge)
            setattr(value, f'{self.name}.discharge', self.discharge)

        super().__setattr__(name, value)

    def locate(self, *locs: Loc):
        """Locate the storage"""
        # update the locations at which the storage exists

        # get location, time tuples where operation is defined
        loc_times = []
        for loc in locs:

            # check if the storage has been capacitated at that location first
            if not self in self.tree.capacitated_at or not loc in [
                l_t[0] for l_t in self.tree.capacitated_at[self]
            ]:
                # # The model could be an only scheduling model
                # if not self.tree.inventoried_at:
                # if the storage is not capacitated at the location and time
                print(
                    f'--- Assuming  {self} capacity is unbounded in ({loc}, {self.horizon})'
                )
                # this is not a check, this generates a constraint
                _ = self.model.invcapacity(self.stored, loc, self.horizon) == True

            # now that the process has been capacitated at the location
            # check if it is being operated at the location

            if not self in self.tree.inventoried_at or not loc in [
                l_t[0] for l_t in self.tree.inventoried_at[self]
            ]:
                # if not just write opr_{pro, loc, horizon} <= capacity_{pro, loc, horizon}
                print(
                    f'--- Assuming inventory of {self.stored} is bound by capacity in ({loc}, {self.horizon})'
                )
                _ = self.model.inventory(self.stored, loc, self.horizon) <= 1

            for d in self.model.inventory.domains:
                if d.operation in [self.charge, self.discharge] and d.space == loc:
                    loc_time = (loc, d.time)
                    if loc_time not in loc_times:
                        loc_times.append(loc_time)

        # locate the charge and discharge processes
        self.charge.locate(*locs)
        self.discharge.locate(*locs)

        # self.writecons_conversion(loc_times)

    @property
    def capacity(self) -> Bind:
        """Reports invcapacity as capacity"""
        return self.invcapacity

    @property
    def base(self) -> Resource:
        """Base resource"""
        return self.discharge.conv.base

    @property
    def conversion(self) -> dict[Resource : int | float]:
        """Conversion of commodities"""
        return self.discharge.conv.conversion

    def __call__(self, resource: Resource | Conv):
        """Conversion is called with a Resource to be converted"""
        if not self._conv:
            # create storage resource
            stored = Resource()
            setattr(self.model, f'{resource}.{self}', stored)

            # ---------- set discharge conversion
            self.discharge.conv = Conv(
                process=self.discharge, storage=self, resource=stored
            )
            _ = self.discharge.conv(resource) == -1.0 * stored

            # ---------- set charge conversion
            self.charge.conv = Conv(
                process=self.charge, storage=self, resource=resource
            )

            _ = self.charge.conv(stored) == -1.0 * resource

            setattr(self.base, self.name, stored)

            self.stored, self.stored.base = stored, self.base
            self._conv = True
            # self.model.update_grb_aspects(add=self.stored)

            # self.model.update_grb(add=self.stored)
        return self.discharge.conv(resource)

    # def writecons_conversion(self, loc_times: list[tuple[Loc, Period]]):
    #     """Write the conversion constraints for the process"""
    #     self.charge.conv.balancer()
    #     self.discharge.conv.balancer()

    #     def time_checker(res: Resource, loc: Loc, time: Period):
    #         """This checks if it is actually necessary
    #         to write conversion at denser temporal scales
    #         """

    #         # This checks whether some other aspect is defined at
    #         # a lower temporal scale
    #         if self.model.grb[res][loc][time]:
    #             return time
    #         else:
    #             return time.horizon

    #     for loc_time in loc_times:
    #         loc = loc_time[0]
    #         time = loc_time[1]

    #         if loc in self.locs:
    #             # if the location is already balanced, skip

    #             continue

    #         time = time_checker(self.stored, loc, time)

    #         # inventory in current time period
    #         # inv = self.model.inventory(self.stored, self, loc, time)
    #         inv = self.stored.inventory(self, loc, time)

    #         v_inv = inv.V(write_grb=True)

    #         # operate in current time period
    #         opr = self.model.operate(self, loc, time)
    #         v_opr = opr.V()

    #         # create an operating constraint
    #         _cons_opr = f'operate_{self}_{loc}_{time}_bal'

    #         cons_opr = v_opr - v_inv == 0
    #         cons_opr.categorize('Flow')
    #         setattr(self.program, _cons_opr, cons_opr)

    #         inv.domain.update_cons(_cons_opr)
    #         self.model.inventory.constraints.append(_cons_opr)
    #         self.model.operate.constraints.append(_cons_opr)

    #         # add previous step inventory to the resource balance
    #         _cons_inv = f'{self.stored}_{loc}_{time}_grb'

    #         cons_inv = getattr(self.program, _cons_inv)

    #         # inventory in previous time period

    #         # inv_t = self.model.inventory(self.stored, self, loc, -1 * time)
    #         inv_t = self.stored.inventory(self.stored, self, loc, -1 * time)

    #         v_inv_t = inv_t.V()

    #         setattr(self.program, _cons_inv, cons_inv + v_inv_t)

    #         self.locs.append(loc)

    #     self.charge.writecons_conversion(loc_times)
    #     self.discharge.writecons_conversion(loc_times)
