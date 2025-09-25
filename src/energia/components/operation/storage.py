"""Storage - Stashes Resource to Withdraw Later"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ...core.component import Component
from ...modeling.parameters.conversion import Conversion
from ..commodity.stored import Stored
from .process import Process

if TYPE_CHECKING:
    from ...modeling.constraints.bind import Bind
    from ..spatial.location import Location


@dataclass
class Storage(Component):  # , Stock):
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
        self.locs: list[Location] = []

    def __setattr__(self, name, value):
        if name == 'model' and value:
            setattr(value, f'{self.name}.charge', self.charge)
            setattr(value, f'{self.name}.discharge', self.discharge)

        super().__setattr__(name, value)

    def locate(self, *locs: Location):
        """Locate the storage"""
        # update the locations at which the storage exists

        # get location, time tuples where operation is defined
        loc_times = []
        for loc in locs:

            if loc not in self.model.invcapacity.bound_spaces[self.stored]:
                # check if the storage capacity has been bound at that location
                print(
                    f'--- Assuming  {self.stored} inventory capacity is unbounded in ({loc}, {self.horizon})'
                )
                # this is not a check, this generates a constraint
                _ = self.capacity(loc, self.horizon) == True

            if self.stored not in self.model.inventory.bound_spaces:
                _ = self.model.inventory(self.stored) == True

            if loc not in self.model.inventory.bound_spaces[self.stored]:
                # check if the storage inventory has been bound at that location
                print(
                    f'--- Assuming inventory of {self.stored} is bound by inventory capacity in ({loc}, {self.horizon})'
                )
                try:
                    times = list(
                        [
                            t
                            for t in self.model.grb[self.stored.inv_of][loc]
                            if self.model.grb[self.stored.inv_of][loc][t]
                        ]
                    )
                except KeyError:
                    times = []
                # write the conversion balance at
                # densest temporal scale in that space
                if times:
                    time = min(times)
                else:
                    time = self.horizon
                # if not just write opr_{pro, loc, horizon} <= capacity_{pro, loc, horizon}
                print(
                    f'--- Assuming inventory of {self.stored} is bound by inventory capacity in ({loc}, {time})'
                )
                _ = self.inventory(loc, time) <= 1

        # locate the charge and discharge processes
        self.charge.locate(*locs)
        self.discharge.locate(*locs)

        # self.writecons_conversion(loc_times)

    @property
    def capacity(self) -> Bind:
        """Reports invcapacity as capacity"""
        return self.stored.invcapacity

    @property
    def setup(self) -> Bind:
        """Reports invsetup as setup"""
        return self.stored.invsetup

    @property
    def dismantle(self) -> Bind:
        """Reports invdismantle as dismantle"""
        return self.stored.invdismantle

    @property
    def inventory(self) -> Bind:
        """Inventory of the stored resource"""
        return self.stored.inventory

    @property
    def base(self) -> Resource:
        """Base resource"""
        return self.discharge.conv.base

    @property
    def conversion(self) -> dict[Resource, int | float]:
        """Conversion of commodities"""
        return self.discharge.conv.conversion

    @property
    def fab(self) -> Conversion:
        """Fabrication conversion of commodities"""
        return self.charge.fab

    def __call__(self, resource: Stored | Conversion):
        """Conversion is called with a Resource to be converted"""
        if not self._conv:
            # create storage resource
            stored = Stored()
            resource.in_inv.append(stored)

            setattr(self.model, f'{resource}.{self}', stored)

            # ---------- set discharge conversion
            self.discharge.conv = Conversion(operation=self.discharge, resource=stored)
            _ = self.discharge.conv(resource) == -1.0 * stored

            # ---------- set charge conversion
            self.charge.conv = Conversion(operation=self.charge, resource=resource)

            _ = self.charge.conv(stored) == -1.0 * resource

            setattr(self.base, self.name, stored)

            self.stored, self.stored.inv_of = stored, self.base
            self._conv = True
            # self.model.update_grb_aspects(add=self.stored)

            # self.model.update_grb(add=self.stored)
        return self.discharge.conv(resource)
