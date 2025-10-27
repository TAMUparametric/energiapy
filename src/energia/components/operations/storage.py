"""Storage - Stashes Resource to Withdraw Later"""

from __future__ import annotations

import logging
from functools import cached_property
from typing import TYPE_CHECKING

from ..._core._component import _Component
from ...modeling.constraints.calculate import Calculate
from ...modeling.parameters.conversion import Conversion
from ...utils.decorators import timer
from ..commodities.resource import Resource
from .process import Process

logger = logging.getLogger("energia")

if TYPE_CHECKING:
    from gana.sets.constraint import C

    from ...components.temporal.periods import Periods
    from ...modeling.variables.aspect import Aspect
    from ...modeling.variables.sample import Sample
    from ..spatial.location import Location


# * Storage is made up of three components:


# Resource in Storage
class Stored(Resource):
    """Resource in Storage"""

    def __init__(self, *args, **kwargs):
        Resource.__init__(self, *args, **kwargs)

        # self.inv_of: Resource | None = None


# A charging process to convert Resource into Stored
class Charge(Process):
    """Process that Charges Storage"""

    def __init__(self, storage: Storage, *args, **kwargs):

        self.storage = storage
        super().__init__(*args, **kwargs)


# A discharging process to convert Stored back into Resource
class Discharge(Process):
    """Process that Discharges Storage"""

    def __init__(self, storage: Storage, *args, **kwargs):

        self.storage = storage
        super().__init__(*args, **kwargs)


class Storage(_Component):
    """
    Storage is a container for three main elements:
    1. A Stored resource
    2. A charge Process that puts the resource into storage
    3. A discharge Process that withdraws the resource from storage

    :param basis: Unit basis of the component. Defaults to None.
    :type basis: Unit, optional
    :param label: An optional label for the component. Defaults to None.
    :type label: str, optional
    :param citations: An optional citation or description for the component. Defaults to None.
    :type citations: str | list[str] | dict[str, str | list[str]], optional
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
    :ivar conversion: Operational conversion associated with the storage. Defaults to None.
    :vartype conversion: Conversion, optional
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
        *args,
        label: str = "",
        citations: str = "",
        **kwargs,
    ):

        _Component.__init__(self, label=label, citations=citations, **kwargs)

        # Charging, Discharging, and Stored Resource (Inventory)
        self.charge: Charge | None = None
        self.discharge: Discharge | None = None
        self.stored: Stored | None = None

        # prevents repeated
        self._birthed = False

        self.locations: list[Location] = []

        self.conversions = args

        self.construction = Conversion(
            operation=self,
            aspect='invcapacity',
            add="dispose",
            sub="use",
            attr_name="construction",
            use_max_time=True,
        )

    @cached_property
    def space_times(self) -> list[tuple[Location, Periods]]:
        """List of location, time tuples where storage is located"""
        return self.charge.space_times

    @cached_property
    def capacity_aspect(self) -> Aspect:
        """Reports invcapacity as aspect"""
        return getattr(self.model, 'invcapacity')

    @cached_property
    def inventory_aspect(self) -> Aspect:
        """Reports inventory as aspect"""
        return getattr(self.model, 'inventory')

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
    def basis(self) -> Resource:
        """Base resource"""
        return self.discharge.production.basis

    @property
    def storage_cost(self) -> Calculate:
        """Cost of storing the resource"""
        return self.inventory[self.model._cash().spend]

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

    @timer(logger, kind='assume-capacity', level=logging.INFO)
    def _check_capacity_bound(self, space: Location) -> bool:
        """Check if the storage capacity has been bound at that location"""

        if self not in self.capacity_aspect.bound_spaces:
            # ensure that the bound spaces dict exists
            self.capacity_aspect.bound_spaces[self.stored] = {"ub": [], "lb": []}

        if space not in self.capacity_aspect.bound_spaces[self.stored]["ub"]:
            # check if the storage capacity has been bound at that location
            # Note: this is not a check, this generates a constraint
            _ = self.capacity(space, self.horizon) == True

            return self, space, self.horizon

        return False

    @timer(logger, kind='assume-inventory', level=logging.INFO)
    def _check_inventory_bound(self, space: Location) -> bool:
        """Check if the storage inventory is capacity bound at that location"""
        if self.stored not in self.inventory_aspect.bound_spaces:
            _ = self.inventory_aspect(self.stored) == True

        if space not in self.inventory_aspect.bound_spaces[self.stored]["ub"]:
            # check if the storage inventory has been bound at that location
            try:
                times = list(
                    [
                        t
                        for t in self.model.balances[self.stored.inv_of][space]
                        if self.model.balances[self.stored.inv_of][space][t]
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
            _ = self.inventory(space, time) <= 1
            return self, space, time

        return False

    @timer(logger, kind="construction")
    def write_construction(
        self,
        space_times: list[tuple[Location, Periods]],
        # fabrication: dict[Resource, int | float | list[int | float]],
    ):
        """write fabrication constraints for the operation"""

        self.construction.balancer()

        for location, time in space_times:
            self.construction.write(location, time)

        return self, (l for l, _ in space_times)

    @timer(logger, kind='locate')
    def locate(self, *spaces: Location):
        """Locate the storage"""
        # update the locations at which the storage exists

        # get location, time tuples where operation is defined
        for space in spaces:

            self._check_capacity_bound(space)

            self._check_inventory_bound(space)

        # locate the charge and discharge processes
        self.charge.locate(*spaces)
        self.discharge.locate(*spaces)

        if self.construction is not None:
            self.write_construction(self.space_times)

        return self, spaces

    def _birth_constituents(
        self,
        charging_args: dict | None = None,
        discharging_args: dict | None = None,
        storage_args: dict | None = None,
    ):
        """Birth the constituents of the storage component"""
        if not self._birthed:
            self.stored = Stored(**storage_args if storage_args else {})

            self.charge = Charge(storage=self, **charging_args if charging_args else {})

            self.discharge = Discharge(
                storage=self, **discharging_args if discharging_args else {}
            )

            # Set them on the model
            setattr(self.model, f"{self.name}.charge", self.charge)
            setattr(self.model, f"{self.name}.discharge", self.discharge)
            setattr(self.model, f"{self.name}.stored", self.stored)

        self._birthed = True

    def _split_attr(self):
        """Splits the parameters dictionary into charging, discharging and storage parameters"""

        _charging_args = {}
        _discharging_args = {}
        _storage_args = {}

        for attr, param in self.parameters.items():
            split_attr = attr.split("_")

            _attr = split_attr[0]

            if _attr == "charge":
                _charging_args["_".join(split_attr[1:])] = param
            elif _attr == "discharge":
                _discharging_args["_".join(split_attr[1:])] = param
            else:
                if attr[:3] == "inv":
                    _storage_args[attr] = param
                else:
                    # if there is no inv prefix.
                    _storage_args["inv" + attr] = param
        # reset parameters to empty
        # none of these go on Storage itself
        self.parameters = {}

        return _charging_args, _discharging_args, _storage_args

    def __setattr__(self, name, value):

        object.__setattr__(self, name, value)

        if name == "model" and value is not None:

            self._birth_constituents(*self._split_attr())

            if self.conversions:

                # if len(self.conversions) > 1:
                #     self.modes =

                for conversion in self.conversions:
                    if not isinstance(conversion, int | float):
                        conversion.operation = self

                if len(self.conversions) == 1:
                    conversion = self.conversions[0]

                    if conversion.hold is not None:
                        _ = self(conversion.resource) == conversion.hold

        super().__setattr__(name, value)

    def __call__(self, resource: Stored | Conversion):
        """Conversion is called with a Resource to be converted"""

        self._birth_constituents()

        _ = self.charge(self.stored) == -resource

        self.discharge.production.expect = self.stored

        self.stored.inv_of = resource

        return self.discharge(resource)
