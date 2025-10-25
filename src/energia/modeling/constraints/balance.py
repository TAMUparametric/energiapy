"""Balance"""

from __future__ import annotations

import logging
import time as keep_time
from operator import is_
from typing import TYPE_CHECKING, Self

from ..._core._hash import _Hash
from ...components.operations.storage import Stored

logger = logging.getLogger("energia")
from ...utils.decorators import timer

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

        self.commodity = self.domain.commodity
        self.samples = self.domain.samples
        self.time = self.domain.time

        self.space = (
            self.domain.linkage.source
            if self.aspect.sign == -1 and self.domain.linkage
            else (
                self.domain.linkage.sink
                if self.domain.linkage
                else self.domain.location
            )
        )

        _ = self.balances[self.commodity][self.space][self.time]

        if not self.samples and self.commodity:
            # if no samples, then create GRB or append to exisiting GRB
            # writecons_grb will figure it out
            self.writecons_grb()
            return

        # if there are samples
        if self.commodity.insitu:
            # # we need to still check if this is this is an insitu (e.g. a storage commodity)
            # if the commodity is insitu that means that
            # no external bounds have been defined
            # a GRB is still needed

            self.writecons_grb()

        if (
            self.aspect(self.commodity, self.time)
            not in self.balances[self.commodity][self.space][self.time]
        ):

            # for the second check, consider the case where

            # # these do not get their own GRB, as they are only utilized within a process

            # if there is already a GRB existing
            # add the bind to the GRB at the same scale
            self.writecons_grb()

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
        # time: Periods,
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

            if len(self.time) == 1:
                return False

            # if inventory is being add to GRB
            lagged_domain = self.domain.change({"lag": -1 * self.time, "periods": None})

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

        self._inform(name)

        return True

    @timer(logger, "Initiating Balance")
    def _create_constraint(self, name: str, stored: bool) -> bool:
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

            if len(self.time) == 1:
                return False

            # TODO: potential bug here
            # this avoids writing inv_ntw_t - inv_ntw_t-1 = 0
            # the need for this check is absurd
            # it ensures that inventory balances are not created for the network directly
            # when location-wise inventory balances can be written
            # this is a temporary fix and needs to be generalized
            if self.model.network.has and self.space.isnetwork:
                # if the location is a network, we cannot have storage
                return False

            # if inventory is being add to GRB
            lagged_domain = self.domain.change({"lag": -1 * self.time, "periods": None})
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
        self._inform(name)

        return self.domain

    def _inform(self, cons_name):
        """
        Updates the constraints in all the indices of self.domain
        Add constraint name to aspect

        :param cons_name: Name of the constraint
        :type cons_name: str
        :param commodity: Commodity being balanced
        :type commodity: Commodity
        :param loc: Location at which the balance is being written
        :type loc: Location
        :param time: Time period at which the balance is being written
        :type time: Periods
        """
        self.domain.update_cons(cons_name)

        if cons_name not in self.aspect.constraints:
            self.aspect.constraints.append(cons_name)

        # update the GRB aspects
        self.balances[self.commodity][self.space][self.time].append(self)

    def writecons_grb(self) -> bool | None:
        """Writes the stream balance constraint

        :param self.commodity: Commodity being balanced
        :type self.commodity: Commodity
        :param self.space: Location at which the balance is being written
        :type self.space: Location
        :param self.time: Time period at which the balance is being written
        :type self.time: Periods

        :returns: False if the constraint was not created or updated
        :rtype: bool | None
        """

        if (
            self.space.isin is not None
            and not self.balances[self.commodity][self.space][self.time]
            and self.balances[self.commodity][self.space.isin][self.time]
        ):
            # if the location is in another location
            # and there is no GRB for that location
            # work with the parent location
            self.space = self.space.isin

        _name = f"{self.commodity}_{self.space}_{self.time}_grb"

        if isinstance(self.commodity, Stored):
            stored = True

        else:
            stored = False
            if self.balances[self.commodity][self.space]:
                # If a GRB exists at a lower temporal order, append to that
                lower_times = [
                    t
                    for t in self.balances[self.commodity][self.space]
                    if t > self.time
                ]

                if lower_times:
                    _ = self.aspect(self.commodity, self.space, lower_times[0]) == True
                    return

        # -initialize GRB for self.commodity if necessary -----

        if not self.balances[self.commodity][self.space][self.time]:
            # this checks whether a general self.commodity balance has been defined
            # for the self.commodity in that space and self.time

            logger.info(
                "Balance for %s in (%s, %s): initializing",
                self.commodity,
                self.space,
                self.time,
            )

            start = keep_time.time()

            made = self._create_constraint(_name, stored)

        # -add aspect to GRB if not added already ----

        # elif self not in self.balances[self.commodity][self.space][self.time]:

        else:

            logger.info(
                "Balance for %s in (%s, %s): adding %s%s",
                self.commodity,
                self.space,
                self.time,
                self.aspect,
                self.domain,
            )

            start = keep_time.time()

            made = self._update_constraint(_name, stored, getattr(self.program, _name))

        if not made:
            return False

        end = keep_time.time()
        logger.info("\u23f1 %s seconds", end - start)

    def __eq__(self, other: Self):
        return is_(self.aspect, other.aspect) and self.domain == other.domain

    def __call__(self, *index: _X):
        """Returns the variable for the aspect at the given index"""
        return self.aspect(*index)
