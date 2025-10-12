"""Balance"""

from __future__ import annotations

import time as keep_time
from dataclasses import dataclass
from operator import is_
from typing import TYPE_CHECKING, Self

from ..._core._generator import _Generator
from ...components.commodity.stored import Stored

if TYPE_CHECKING:
    from gana.sets.function import F

    from ..._core._x import _X
    from ..indices.domain import Domain


@dataclass
class Balance(_Generator):
    """Performs a general commodity balance

    Args:
        aspect (Aspect. optional): Aspect to which the constraint is applied
        domain (Domain. optional): Domain over which the aspect is defined

    Attributes:
        name (str. optional): Name of the constraint.
    """

    def __post_init__(self):

        _Generator.__post_init__(self)

        # this is the disposition of the variable to be mapped
        # through time and space

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

        _ = self.model.grb[commodity][loc][time]

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

    def writecons_grb(self, commodity, loc, time):
        """Writes the stream balance constraint"""

        _name = f"{commodity}_{loc}_{time}_grb"

        # ---- initialize GRB for commodity if necessary -----

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

        if (
            not self.domain.linkage
            and loc.isin
            and commodity in self.grb
            and loc.isin in self.grb[commodity]
        ):

            if (
                loc.isin in self.grb[commodity]
                and time in self.grb[commodity][loc.isin]
                and self.grb[commodity][loc.isin][time]
            ):

                if self.domain.operation:
                    print(
                        f"--- General Resource Balance for {commodity} in ({loc.isin}, {time}): adding {self.aspect} from {self.domain.operation}",
                    )
                else:
                    print(
                        f"--- General Resource Balance for {commodity} in ({loc.isin}, {time}): adding {self.aspect}",
                    )

                start = keep_time.time()

                _name = f"{commodity}_{loc.isin}_{time}_grb"

                cons_grb = getattr(self.program, _name)
                if self.aspect.ispos:  # or _signs[n]:
                    setattr(
                        self.program,
                        _name,
                        cons_grb + self(*self.domain).V(),
                    )
                else:
                    setattr(
                        self.program,
                        _name,
                        cons_grb - self(*self.domain).V(),
                    )

                end = keep_time.time()
                print(f"    Completed in {end-start} seconds")

                self.domain.update_cons(_name)
                if _name not in self.aspect.constraints:
                    self.aspect.constraints.append(_name)

        elif not self.grb[commodity][loc][time]:
            # this checks whether a general commodity balance has been defined
            # for the commodity in that space and time

            # first check if a bind has been defined

            # update the GRB aspects

            self.grb[commodity][loc][time].append(self)

            print(
                f"--- General Resource Balance for {commodity} in ({loc}, {time}): initializing constraint, adding {self.aspect}{self.domain}",
            )
            start = keep_time.time()

            if stored and self.aspect.name == "inventory":
                if len(time) == 1:
                    return

                # if inventory is being add to GRB
                lagged_domain = self.domain.change({"lag": -1 * time, "periods": None})
                cons_grb = -self(*self.domain).V() + self(*lagged_domain).V() == 0
            elif self.aspect.ispos:  # or _signs[n]:
                cons_grb = self(*self.domain).V() == 0
            else:
                cons_grb = -self(*self.domain).V() == 0

            cons_grb.categorize("General Resource Balance")

            setattr(
                self.program,
                _name,
                cons_grb,
            )
            end = keep_time.time()
            print(f"    Completed in {end-start} seconds")

            # updates the constraints in all indices of self.domain
            self.domain.update_cons(_name)
            # add constraint name for aspect
            self.aspect.constraints.append(_name)

        # ---- add aspect to GRB if not added already ----

        elif self not in self.grb[commodity][loc][time]:

            print(
                f"--- General Resource Balance for {commodity} in ({loc}, {time}): adding {self.aspect}{self.domain}",
            )

            start = keep_time.time()

            # update the GRB aspects
            self.grb[commodity][loc][time].append(self)

            # grab the constraint from the program
            cons_grb = getattr(self.program, _name)

            if commodity.in_inv and self.aspect.name == "inventory":
                # if inventory is being add to GRB
                lagged_domain = self.domain.change({"lag": -1 * time, "periods": None})

                setattr(
                    self.program,
                    _name,
                    cons_grb + self(*lagged_domain).V() - self(*self.domain).V(),
                )

            # update the constraint
            elif self.aspect.ispos:
                setattr(
                    self.program,
                    _name,
                    cons_grb + self(*self.domain).V(),
                )
            else:
                setattr(
                    self.program,
                    _name,
                    cons_grb - self(*self.domain).V(),
                )
            end = keep_time.time()
            print(f"    Completed in {end-start} seconds")

            # updates the constraints in all the indices of self.domain
            self.domain.update_cons(_name)
            # add constraint name to aspect
            if _name not in self.aspect.constraints:
                self.aspect.constraints.append(_name)

        # ---- add aspect to GRB if not added already ----

        # check if the commodity is bound at a spatial index of a lower order

    def __eq__(self, other: Self):
        return is_(self.aspect, other.aspect) and self.domain == other.domain

    def __call__(self, *index: _X):
        """Returns the variable for the aspect at the given index"""
        return self.aspect(*index)
