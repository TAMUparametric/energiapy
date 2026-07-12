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
    from gana import V
    from gana.sets.constraint import C
    from gana.sets.function import F

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
    """

    def __init__(self, aspect: Aspect, domain: Domain):
        self.aspect = aspect
        self.domain = domain

        self._handshake()

        self.write()

    def write(self) -> tuple[Domain, Aspect] | Domain | bool | None:
        """Writes the stream balance constraint"""

        if self._check_existing():
            return False

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
        if (
            self._space.isin
            and self.balances[self.commodity][self._space.isin][self.time]
        ):
            # if a balance is written for a parent location, write for parent
            return self._space.isin
        return self._space

    @cached_property
    def _space(self):
        """Location where balance is applied"""
        if self.domain.linkage:
            # if outgoing, apply at sink
            return (
                self.domain.linkage.sink
                if self.aspect.sign == 1
                else self.domain.linkage.source
            )
        return self.domain.location

    @cached_property
    def name(self) -> str:
        """Name of the constraint"""
        return f"{self.aspect.name}{self.domain}"

    @cached_property
    def cons_name(self) -> str:
        """Name of the constraint"""
        return f"{self.commodity}_{self.space}_{self.time}_grb"

    @property
    def existing_aspects(self):
        """Exisiting Aspects"""
        return self.balances[self.commodity][self.space][self.time]

    @cached_property
    def updated_part(self) -> V | F | int:
        """Returns the part of the constraint that is new"""
        if self.stored and self.aspect == "inventory":
            # if inventory is being add to GRB
            if len(self.time) == 1:
                # cannot lag a single time period
                return 0

            return (
                self(*self.domain).V()
                - self(*self.domain.edit({"lag": -1 * self.time, "periods": None})).V()
            )

        return self(*self.domain).V()

    @timer(logger, "balance-init")
    def _birth_constraint(self) -> Domain | bool:
        """
        Births a new General Resource Balance constraint

        :returns: Domain if constraint is created, else False
        :rtype: Domain | bool
        """

        cons_grb = (
            self.updated_part == 0 if self.aspect.ispos else -self.updated_part == 0
        )

        if cons_grb is True:
            # this catches the case where 0 is returned by fresh_part
            # making cons_grb, 0 == 0, i.e. True
            return False

        cons_grb.categorize("Balance")

        setattr(
            self.program,
            self.cons_name,
            cons_grb,
        )
        self._inform()

        return self.domain

    @timer(logger, "balance-update")
    def _update_constraint(
        self,
    ) -> tuple[Domain, Aspect]:
        """
        Updates an existing General Resource Balance constraint

        :returns: The domain and aspect of the updated constraint for logging purposes
        :rtype: tuple[Domain, Aspect]
        """

        cons_grb: C = getattr(self.program, self.cons_name)

        setattr(
            self.program,
            self.cons_name,
            (
                cons_grb + self.updated_part
                if self.aspect.ispos
                else cons_grb - self.updated_part
            ),
        )

        self._inform()

        # this is returned for logging purposes
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
        self.domain.inform_components_of_cons(self.cons_name)

        self.aspect.constraints.add(self.cons_name)

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

        lower_times = [t for t in _balances if t > self.time] if _balances else False

        if lower_times:
            _ = self.aspect(self.commodity, self.space, lower_times[0]) >= 0

    def __eq__(self, other: Self):
        return is_(self.aspect, other.aspect) and self.domain == other.domain

    def __call__(self, *index: _X):
        """Returns the variable for the aspect at the given index"""
        return self.aspect(*index)
