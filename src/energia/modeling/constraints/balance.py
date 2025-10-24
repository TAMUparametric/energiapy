"""Balance"""

from __future__ import annotations

import logging
import time as keep_time
from operator import is_
from typing import TYPE_CHECKING, Self

from ..._core._hash import _Hash
from ...components.operation.storage import Stored

logger = logging.getLogger("energia")

if TYPE_CHECKING:
    from gana.sets.constraint import C

    from ..._core._x import _X
    from ...components.spatial.linkage import Linkage
    from ...components.spatial.location import Location
    from ...components.temporal.periods import Periods
    from ..indices.domain import Domain
    from ..variables.aspect import Aspect


class Balance(_Hash):
    """Performs a general commodity balance

    :param aspect: Aspect to which the constraint is applied
    :type aspect: Aspect
    :param domain: Domain over which the aspect is defined
    :type domain: Domain
    :param label: Label for the constraint. Defaults to "".
    :type label: str

    :ivar model: The model to which the component belongs.
    :vartype model: Model
    :ivar program: The program to which the constraint belongs.
    :vartype program: Program
    :ivar grb: The general resource balance dictionary.
    :vartype grb: dict[Commodity, dict[Location, dict[Periods, list[Aspect]]]]
    """

    def __init__(self, aspect: Aspect, domain: Domain, label: str = ""):
        self.aspect = aspect
        self.domain = domain
        self.label = label

        self.model = self.aspect.model
        self.program = self.model.program
        self.balances = self.model.balances

        if self.domain.modes:
            return

        commodity = self.domain.commodity
        samples = self.domain.samples
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

        _ = self.balances[commodity][loc][time]

        if not samples and commodity:
            # if no samples, then create GRB or append to exisiting GRB
            # writecons_grb will figure it out
            self.writecons_grb(commodity, loc, time)
            return

        # if there are samples
        if commodity.insitu:
            # # we need to still check if this is this is an insitu (e.g. a storage commodity)
            # if the commodity is insitu that means that
            # no external bounds have been defined
            # a GRB is still needed

            self.writecons_grb(commodity, loc, time)

        if self.aspect(commodity, loc, time) not in self.balances[commodity][loc][time]:

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
        """
        Updates an existing GRB constraint with the new aspect

        :param name: Name of the constraint
        :type name: str
        :param stored: If the commodity is stored
        :type stored: bool
        :param time: Time period of the constraint
        :type time: Periods
        :param cons_grb: The existing GRB constraint
        :type cons_grb: C

        :returns: If the constraint was updated
        :rtype: bool
        """
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
        """
        Creates a new GRB constraint

        :param name: Name of the constraint
        :type name: str
        :param stored: If the commodity is stored
        :type stored: bool
        :param time: Time period of the constraint
        :type time: Periods
        :param space: Location or Linkage of the constraint
        :type space: Location | Linkage

        :returns: If the constraint was created
        :rtype: bool
        """

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

        cons_grb.categorize("Balance")

        setattr(
            self.program,
            name,
            cons_grb,
        )

        return True

    def writecons_grb(self, commodity, loc, time) -> bool | None:
        """Writes the stream balance constraint

        :param commodity: Commodity being balanced
        :type commodity: Commodity
        :param loc: Location at which the balance is being written
        :type loc: Location
        :param time: Time period at which the balance is being written
        :type time: Periods

        :returns: False if the constraint was not created or updated
        :rtype: bool | None
        """

        if (
            loc.isin is not None
            and not self.balances[commodity][loc][time]
            and self.balances[commodity][loc.isin][time]
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
            if self.balances[commodity][loc]:
                # If a GRB exists at a lower temporal order, append to that
                lower_times = [t for t in self.balances[commodity][loc] if t > time]

                if lower_times:
                    _ = self.aspect(commodity, loc, lower_times[0]) == True
                    return

        # -initialize GRB for commodity if necessary -----

        if not self.balances[commodity][loc][time]:
            # this checks whether a general commodity balance has been defined
            # for the commodity in that space and time

            logger.info(
                "Balance for %s in (%s, %s): initializing", commodity, loc, time
            )

            start = keep_time.time()

            made = self._create_constraint(_name, stored, time, loc)

        # -add aspect to GRB if not added already ----

        # elif self not in self.balances[commodity][loc][time]:

        else:

            logger.info(
                "Balance for %s in (%s, %s): adding %s%s",
                commodity,
                loc,
                time,
                self.aspect,
                self.domain,
            )

            start = keep_time.time()

            made = self._update_constraint(
                _name, stored, time, getattr(self.program, _name)
            )

        if not made:
            return False

        end = keep_time.time()
        logger.info("\u2714 Completed in %s seconds", end - start)
        # updates the constraints in all the indices of self.domain
        # add constraint name to aspect
        self.domain.update_cons(_name)

        if _name not in self.aspect.constraints:
            self.aspect.constraints.append(_name)

        # update the GRB aspects
        self.balances[commodity][loc][time].append(self)

    def __eq__(self, other: Self):
        return is_(self.aspect, other.aspect) and self.domain == other.domain

    def __call__(self, *index: _X):
        """Returns the variable for the aspect at the given index"""
        return self.aspect(*index)
