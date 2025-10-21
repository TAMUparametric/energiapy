"""Storage - Stashes Resource to Withdraw Later"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from ..._core._component import _Component
from ...modeling.constraints.calculate import Calculate
from ...modeling.parameters.conversion import Conversion
from ..commodity.stored import Stored
from .process import Process

logger = logging.getLogger("energia")

if TYPE_CHECKING:
    from gana.sets.constraint import C

    from ...modeling.variables.sample import Sample
    from ..commodity.resource import Resource
    from ..measure.unit import Unit
    from ..spatial.location import Location


class Storage(_Component):
    """
    Storage

    :param basis: Unit basis of the component. Defaults to None.
    :type basis: Unit, optional
    :param label: An optional label for the component. Defaults to None.
    :type label: str, optional
    :param captions: An optional citation or description for the component. Defaults to None.
    :type captions: str | list[str] | dict[str, str | list[str]], optional
    :param store: The resource to be stored. Defaults to None.
    :type store: Resource, optional

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
    :ivar stored: The resource being stored. Defaults to None.
    :vartype stored: Stored, optional
    :ivar conv: Operational conversion associated with the storage. Defaults to None.
    :vartype conv: Conversion, optional
    :ivar _conv: True if the operational conversion has been set. Defaults to False.
    :vartype _conv: bool
    :ivar charge: The charge process associated with the storage.
    :vartype charge: Process
    :ivar discharge: The discharge process associated with the storage.
    :vartype discharge: Process
    :ivar locations: List of locations where the storage is located. Defaults to [].
    :vartype locations: list[Location]
    """

    def __init__(
        self,
        store: Resource | None = None,
        basis: Unit | None = None,
        label: str = "",
        captions: str = "",
        **kwargs,
    ):

        _Component.__init__(self, basis=basis, label=label, captions=captions, **kwargs)

        self.stored = store
        self.charge = Process()
        self.charge.ofstorage = self
        self.discharge = Process()
        self.discharge.ofstorage = self
        self.locations: list[Location] = []

    def __setattr__(self, name, value):
        if name == "model" and value is not None:
            setattr(value, f"{self.name}.charge", self.charge)
            setattr(value, f"{self.name}.discharge", self.discharge)

        super().__setattr__(name, value)

    def locate(self, *locations: Location):
        """Locate the storage"""
        # update the locations at which the storage exists

        # get location, time tuples where operation is defined
        for loc in locations:

            if self not in self.model.invcapacity.bound_spaces:
                self.model.invcapacity.bound_spaces[self.stored] = {"ub": [], "lb": []}

            if loc not in self.model.invcapacity.bound_spaces[self.stored]["ub"]:
                # check if the storage capacity has been bound at that location

                logger.info(
                    f"Assuming  {self.stored} inventory capacity is unbounded in ({loc}, {self.horizon})",
                )
                # this is not a check, this generates a constraint
                _ = self.capacity(loc, self.horizon) == True

            if self.stored not in self.model.inventory.bound_spaces:
                _ = self.model.inventory(self.stored) == True

            if loc not in self.model.inventory.bound_spaces[self.stored]["ub"]:
                # check if the storage inventory has been bound at that location
                logger.info(
                    f"Assuming inventory of {self.stored} is bound by inventory capacity in ({loc}, {self.horizon})",
                )
                try:
                    times = list(
                        [
                            t
                            for t in self.model.grb[self.stored.inv_of][loc]
                            if self.model.grb[self.stored.inv_of][loc][t]
                        ],
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
                logger.info(
                    f"Assuming inventory of {self.stored} is bound by inventory capacity in ({loc}, {time})",
                )

                _ = self.inventory(loc, time) <= 1

        # locate the charge and discharge processes
        self.charge.locate(*locations)
        self.discharge.locate(*locations)

        # self.writecons_conversion(loc_times)

    @property
    def capacity(self) -> Sample:
        """Reports invcapacity as capacity"""
        return self.stored.invcapacity

    @property
    def setup(self) -> Sample:
        """Reports invsetup as setup"""
        return self.stored.invsetup

    @property
    def dismantle(self) -> Sample:
        """Reports invdismantle as dismantle"""
        return self.stored.invdismantle

    @property
    def inventory(self) -> Sample:
        """Inventory of the stored resource"""
        return self.stored.inventory

    @property
    def capex(self) -> Calculate:
        """Capital Expenditure"""
        return self.capacity[self.model.default_currency().spend]

    @property
    def opex(self) -> Calculate:
        """Operational Expenditure"""
        return self.charge.operate[self.model.default_currency().spend]

    @property
    def base(self) -> Resource:
        """Base resource"""
        return self.discharge.conversion._basis

    @property
    def storage_cost(self) -> Calculate:
        """Cost of storing the resource"""
        return self.inventory[self.model.default_currency().spend]

    @property
    def cons(self) -> list[C]:
        """Constraints"""
        # This overwrites the Component cons property
        # this gets the actual constraint objects from the program
        # based on the pname (attribute name) in the program
        return (
            [getattr(self.program, c) for c in self.constraints]
            + self.charge.cons
            + self.discharge.cons
            + self.stored.cons
        )

    @property
    def fab(self) -> Conversion:
        """Fabrication conversion of commodities"""
        return self.charge.fab

    def __call__(self, resource: Stored | Conversion):
        """Conversion is called with a Resource to be converted"""
        # create storage resource
        stored = Stored()
        resource.in_inv.append(stored)

        setattr(self.model, f"{resource}.{self}", stored)

        # -------set discharge conversion
        self.discharge.conversion = Conversion(operation=self.discharge, basis=stored)
        _ = self.discharge.conversion(resource) == -1.0 * stored

        # -------set charge conversion
        self.charge.conversion = Conversion(operation=self.charge, basis=resource)

        _ = self.charge.conversion(stored) == -1.0 * resource

        setattr(self.discharge.conversion._basis, self.name, stored)

        self.stored, self.stored.inv_of = stored, self.discharge.conversion._basis

        return self.discharge.conversion(resource)
