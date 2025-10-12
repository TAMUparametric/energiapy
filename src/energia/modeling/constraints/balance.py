"""Balance"""

from __future__ import annotations

import time as keep_time
from operator import is_
from typing import TYPE_CHECKING, Self

from ...components.commodity.stored import Stored

if TYPE_CHECKING:
    from gana.sets.constraint import C

    from ..._core._x import _X
    from ...components.spatial.linkage import Linkage
    from ...components.spatial.location import Location
    from ...components.temporal.periods import Periods
    from ..indices.domain import Domain
    from ..variables.aspect import Aspect


class Balance:
    """Performs a general commodity balance

    Args:
        aspect (Aspect. optional): Aspect to which the constraint is applied
        domain (Domain. optional): Domain over which the aspect is defined

    Attributes:
        name (str. optional): Name of the constraint.
    """

    def __init__(self, aspect: Aspect, domain: Domain, label: str = ""):
        self.aspect = aspect
        self.domain = domain
        self.label = label

        self.model = self.aspect.model
        self.program = self.model.program
        self.grb = self.model.grb

        if self.domain.modes:
            return

        commodity = self.domain.commodity
        binds = self.domain.binds
        time = self.domain.time

        loc = (
            self.domain.linkage.source
            if self.aspect.sign == -1 and self.domain.linkage
            else (
                self.domain.linkage.sink
                if self.domain.linkage
                else self.domain.location
            )
        )

        _ = self.grb[commodity][loc][time]

        if not binds and commodity:
            # if no binds, then create GRB or append to exisiting GRB
            # writecons_grb will figure it out
            self.writecons_grb(commodity, loc, time)
            return

        # if there are binds
        if commodity.insitu:
            # # we need to still check if this is this is an insitu (e.g. a storage commodity)
            # if the commodity is insitu that means that
            # no external bounds have been defined
            # a GRB is still needed

            self.writecons_grb(commodity, loc, time)

        if self.aspect(commodity, loc, time) not in self.grb[commodity][loc][time]:
            # for the second check, consider the case where

            # # these do not get their own GRB, as they are only utilized within a process

            # if there is already a GRB existing
            # add the bind to the GRB at the same scale
            self.writecons_grb(commodity, loc, time)

    @property
    def name(self) -> str:
        """Name of the constraint"""
        return f"{self.aspect.name}{self.domain}"

    @property
    def mapped_to(self) -> list[Domain]:
        """List of domains that the aspect has been mapped to"""
        return self.aspect.maps

    @property
    def sign(self) -> float:
        """Returns the aspect"""
        return self.aspect.sign

    def _update_constraint(
        self,
        name: str,
        stored: bool,
        time: Periods,
        cons_grb: C,
    ) -> bool:
        """Updates an existing GRB constraint with the new aspect"""
        if stored and self.aspect.name == "inventory":

            if len(time) == 1:
                return False

            # if inventory is being add to GRB
            lagged_domain = self.domain.change({"lag": -1 * time, "periods": None})

            setattr(
                self.program,
                name,
                cons_grb + self(*lagged_domain).V() - self(*self.domain).V(),
            )
        else:
            setattr(
                self.program,
                name,
                (
                    cons_grb + self(*self.domain).V()
                    if self.aspect.ispos
                    else cons_grb - self(*self.domain).V()
                ),
            )

        return True

    def _create_constraint(
        self, name: str, stored: bool, time: Periods, space: Location | Linkage
    ) -> bool:
        """Creates a new GRB constraint"""

        if stored and self.aspect.name == "inventory":

            if len(time) == 1:
                return False

            # TODO: potential bug here
            # this avoids writing inv_ntw_t - inv_ntw_t-1 = 0
            # the need for this check is absurd
            # it ensures that inventory balances are not created for the network directly
            # when location-wise inventory balances can be written
            # this is a temporary fix and needs to be generalized
            if self.model.network.has and space.isnetwork:
                # if the location is a network, we cannot have storage
                return False

            # if inventory is being add to GRB
            lagged_domain = self.domain.change({"lag": -1 * time, "periods": None})
            cons_grb = -self(*self.domain).V() + self(*lagged_domain).V() == 0

        else:
            cons_grb = (
                self(*self.domain).V() == 0
                if self.aspect.ispos
                else -self(*self.domain).V() == 0
            )

        cons_grb.categorize("General Resource Balance")

        setattr(
            self.program,
            name,
            cons_grb,
        )

        return True

    def writecons_grb(self, commodity, loc, time):
        """Writes the stream balance constraint"""

        if (
            loc.isin is not None
            and not self.grb[commodity][loc][time]
            and self.grb[commodity][loc.isin][time]
        ):
            # if the location is in another location
            # and there is no GRB for that location
            # work with the parent location
            loc = loc.isin

        _name = f"{commodity}_{loc}_{time}_grb"

        if isinstance(commodity, Stored):
            stored = True

        else:
            stored = False

            if self.grb[commodity][loc]:
                # If a GRB exists at a lower temporal order, append to that
                lower_times = [t for t in self.grb[commodity][loc] if t > time]
                if lower_times:
                    _ = self.aspect(commodity, loc, lower_times[0]) == True
                    return

        # ---- initialize GRB for commodity if necessary -----

        if not self.grb[commodity][loc][time]:
            # this checks whether a general commodity balance has been defined
            # for the commodity in that space and time

            print(
                f"--- General Resource Balance for {commodity} in ({loc}, {time}): initializing constraint, adding {self.aspect}{self.domain}",
            )

            start = keep_time.time()

            made = self._create_constraint(_name, stored, time, loc)

        # ---- add aspect to GRB if not added already ----

        # elif self not in self.grb[commodity][loc][time]:

        else:

            print(
                f"--- General Resource Balance for {commodity} in ({loc}, {time}): adding {self.aspect}{self.domain}",
            )

            start = keep_time.time()

            made = self._update_constraint(
                _name, stored, time, getattr(self.program, _name)
            )

        if not made:
            return

        end = keep_time.time()
        print(f"    Completed in {end-start} seconds")

        # updates the constraints in all the indices of self.domain
        # add constraint name to aspect
        self.domain.update_cons(_name)

        if _name not in self.aspect.constraints:
            self.aspect.constraints.append(_name)

        # update the GRB aspects
        self.grb[commodity][loc][time].append(self)

    def __eq__(self, other: Self):
        return is_(self.aspect, other.aspect) and self.domain == other.domain

    def __call__(self, *index: _X):
        """Returns the variable for the aspect at the given index"""
        return self.aspect(*index)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)
