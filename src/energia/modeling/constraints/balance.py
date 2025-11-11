"""Balance"""

from __future__ import annotations

import logging
from functools import cached_property
from operator import is_
from typing import TYPE_CHECKING, Self

from ..._core._hash import _Hash
from ...components.operations.storage import Stored
from ...utils.decorators import timer

logger = logging.getLogger("energia")

if TYPE_CHECKING:
    from gana.sets.constraint import C

    from ..._core._x import _X
    from ...components.spatial.linkage import Linkage
    from ...components.spatial.location import Location
    from ..indices.domain import Domain
    from ..variables.aspect import Aspect


class Balance(_Hash):
    """Performs a general commodity balance

    :param aspect: Aspect to which the constraint is applied
    :type aspect: Aspect
    :param domain: Domain over which the aspect is defined
    :type domain: Domain

    :ivar model: The model to which the component belongs.
    :vartype model: Model
    :ivar program: The program to which the constraint belongs.
    :vartype program: Program
    :ivar grb: The general resource balance dictionary.t
    :vartype grb: dict[Commodity, dict[Location, dict[Periods, list[Aspect]]]]
    """

    def __init__(self, aspect: Aspect, domain: Domain):
        self.aspect = aspect
        self.domain = domain

        self._handshake()

        self.write()

    def write(self) -> Domain | bool | None:
        """Writes the stream balance constraint"""

        if self._check_existing():
            return False

        self._name = f"{self.commodity}_{self.space}_{self.time}_grb"

        if not self.stored:
            self._init_sample()

        if self.existing_aspects:
            # if exists, update
            return self._update_constraint()

        # else, create new
        return self._birth_constraint()

    @cached_property
    def stored(self):
        """If the commodity is a Stored commodity"""
        return isinstance(self.commodity, Stored)

    @cached_property
    def space(self) -> Location | Linkage | None:
        """Location or Linkage of the constraint"""
        _space = (
            self.domain.linkage.source
            if self.aspect.sign == -1 and self.domain.linkage
            else (
                self.domain.linkage.sink
                if self.domain.linkage
                else self.domain.location
            )
        )

        if (
            _space.isin is not None
            and self.balances[self.commodity][_space.isin][self.time]
        ):

            return _space.isin
        return _space

    @cached_property
    def name(self) -> str:
        """Name of the constraint"""
        return f"{self.aspect.name}{self.domain}"

    @property
    def existing_aspects(self):
        """Exisiting Aspects"""
        return self.balances[self.commodity][self.space][self.time]

    @timer(logger, "balance-init")
    def _birth_constraint(self) -> Domain | bool:
        """
        Creates a new GRB constraint

        :param stored: If the commodity is stored
        :type stored: bool

        :returns: Domain in which the constraint was created
        :rtype: Domain
        """

        # The reason this is avoided is:
        # inv(t) - inv(t-1)  = #charge_eff*p_charge - #charge_eff*p_dcharge
        # for one time period, this becomes
        # inv(t) = #charge_eff*p_charge - #charge_eff*p_dcharge
        # if inv cost is not provided, this can become unbounded
        # or bounded to the max capacity
        if self.stored and self.aspect.name == "inventory":

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
            lagged_domain = self.domain.edit({"lag": -1 * self.time, "periods": None})
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
            self._name,
            cons_grb,
        )
        self._inform()

        return self.domain

    @timer(logger, "balance-update")
    def _update_constraint(
        self,
    ) -> bool:
        """
        Updates an existing GRB constraint with the new aspect

        :param stored: If the commodity is stored
        :type stored: bool
        :param cons_grb: The existing GRB constraint
        :type cons_grb: C

        :returns: If the constraint was updated
        :rtype: bool
        """

        cons_grb: C = getattr(self.program, self._name)

        if self.stored and self.aspect.name == "inventory":

            if len(self.time) == 1:
                return False

            # if inventory is being add to GRB

            lagged_domain = self.domain.edit({"lag": -1 * self.time, "periods": None})

            _update = self(*self.domain).V() - self(*lagged_domain).V()

        else:

            _update = self(*self.domain).V()

        setattr(
            self.program,
            self._name,
            cons_grb + _update if self.aspect.ispos else cons_grb - _update,
        )

        # else:
        #     setattr(
        #         self.program,
        #         self._name,
        #         (
        #             cons_grb + self(*self.domain).V()
        #             if self.aspect.ispos
        #             else cons_grb - self(*self.domain).V()
        #         ),
        #     )

        self._inform()

        return self.domain, self.aspect

    def _check_existing(self) -> bool:
        """Checks if the balance constraint already exists"""
        if (
            (not self.samples and self.commodity)
            or (self.aspect(self.commodity, self.time) not in self.existing_aspects)
            or (self.commodity.insitu)
        ):
            return False
        return True

    def _inform(self):
        """
        Updates the constraints in all the indices of self.domain
        Add constraint name to aspect
        """
        self.domain.inform_components_of_cons(self._name)

        self.aspect.constraints.add(self._name)

        # update the GRB aspects
        self.existing_aspects.append(self)

    def _handshake(self):
        """Borrow attributes from aspect and domain"""
        # take from aspect
        self.model = self.aspect.model

        # take from program
        self.program = self.model.program
        self.balances = self.model.balances

        # take from domain
        self.commodity = self.domain.commodity
        self.samples = self.domain.samples
        self.time = self.domain.time

    def _init_sample(self):
        """Initializes the sample for the balance constraint
        if needed
        """

        _balances = self.balances[self.commodity][self.space]
        if _balances:
            # If a GRB exists at a lower temporal order, append to that

            lower_times = [t for t in _balances if t > self.time]

            if lower_times:
                _ = self.aspect(self.commodity, self.space, lower_times[0]) == True

    def __eq__(self, other: Self):
        return is_(self.aspect, other.aspect) and self.domain == other.domain

    def __call__(self, *index: _X):
        """Returns the variable for the aspect at the given index"""
        return self.aspect(*index)
