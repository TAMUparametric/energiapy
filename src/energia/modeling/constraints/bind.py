"""Bind constraint"""

from __future__ import annotations

import logging
from functools import cached_property
from typing import TYPE_CHECKING

from ...utils.decorators import timer

# from ...components.temporal.modes import Modes
from ...utils.math import normalize

logger = logging.getLogger("energia")

if TYPE_CHECKING:
    from gana.sets.constraint import C

    from ..._core._component import _Component
    from ..._core._x import _X
    from ..variables.sample import Sample


class Bind:
    """Bind constraint

    :param sample: The sample variable to bind
    :type sample: Sample
    :param parameter: The parameter bound
    :type parameter: float | list[float] | dict[float, float] | tuple[float, float] | list[tuple[float, float]]
    :param leq: If True, the sample is constrained to be less than or equal to the bound
    :type leq: bool
    :param geq: If True, the sample is constrained to be greater than or equal to the bound
    :type geq: bool
    :param eq: If True, the sample is constrained to be equal to the bound
    :type eq: bool
    :param forall: If provided, the constraint is applied for all elements in this list
    :type forall: list[_X | _Component] | None

    :ivar model: The model to which the component belongs.
    :vartype model: Model
    :ivar nominal: The nominal value of the sample variable.
    :vartype nominal: float | None
    :ivar norm: If True, the sample variable is normalized.
    :vartype norm: bool
    :ivar domain: The domain of the sample.
    :vartype domain: Domain
    :ivar aspect: The aspect of the sample.
    :vartype aspect: Aspect
    :ivar report: If True, the sample variable is reported.
    :vartype report: bool
    :ivar program: The program to which the sample belongs.
    :vartype program: Prg
    """

    def __init__(
        self,
        sample: Sample,
        parameter: (
            float
            | list[float]
            | dict[float, float]
            | tuple[float, float]
            | list[tuple[float, float]]
        ),
        leq: bool = False,
        geq: bool = False,
        eq: bool = False,
        forall: list[_X | _Component] | None = None,
        parameter_name: str = "",
    ):
        self.sample = sample
        self._parameter = parameter
        self.leq = leq
        self.geq = geq
        self.eq = eq
        self.forall = forall
        self.parameter_name = parameter_name

        # borrowed from Sample
        self.model = sample.model
        self.nominal = sample.nominal
        self.norm = sample.norm
        self.domain = sample.domain
        self.aspect = sample.aspect
        self.report = sample.report
        self.program = sample.program

        # will be written
        self.cons: C = None

        if self.forall:
            # if as set is passed
            # write the constraint 'for all' elements in it
            self._write_forall()
            return

        if isinstance(self._parameter, dict):
            # if a dict is passed, it is assumed to be mode bounds
            self._write_w_modes()
            return

        self.write()

    @cached_property
    def parameter(self):
        """Parameter bound of the bind constraint"""

        if self.nominal:
            # if a nominal value for the self.parameter is passed
            # this is essentially the expectation
            # skipping an instance check here
            # if a non iterable is passed, let an error be raised
            if self.norm:
                _parameter = normalize(self._parameter)

            else:
                _parameter = self._parameter

            # if the sample needs to be normalized
            _parameter = [
                (
                    (self.nominal * i[0], self.nominal * i[1])
                    if isinstance(i, tuple)
                    else self.nominal * i
                )
                for i in _parameter
            ]
            return _parameter

        return self._parameter

    @cached_property
    def lhs(self):
        """Left hand side of the bind constraint"""

        # ------Get LHS
        # lhs needs to be determined here
        # because V will be spaced and timed if not passed by user
        # .X(), .Vb() need time and space
        return self.sample.V(self.parameter)

    @cached_property
    def rhs(self):
        """Right hand side of the bind constraint"""

        if self.aspect.bound is not None:
            # ------if variable bound
            if self.report:
                # ------if variable bound and reported
                # we do not want a bi-linear term
                _rhs = self.parameter * self.sample.X(self.parameter)

            else:
                # ------if just variable bound
                _rhs = self.parameter * self.sample.Vb()

        elif self.report or self.domain.modes is not None:
            # ------if  self.parameter bound and reported or has modes
            # create reporting variable write v <= p*x
            _rhs = self.parameter * self.sample.X(self.parameter)
            self.aspect.update(self.domain, reporting=True)

        else:
            # ------if just self.parameter bound
            _rhs = self.parameter
        return _rhs

    @cached_property
    def rel(self):
        """Constraint name suffix"""

        if self.leq:
            return "ub"
        elif self.eq:
            return "eq"
        elif self.geq:
            return "lb"

    @cached_property
    def cons_name(self):
        """Constraint name"""

        return rf"{self.aspect.name}{self.domain.idxname}_{self.rel}"

    @timer(logger, kind="bind")
    def write(self):
        """Writes the bind constraint"""

        # the lhs comes from the sample
        # calling the lhs here, updates the
        _ = self.lhs

        if self._check_existing():
            return False

        if self.leq:
            self.cons: C = self.lhs <= self.rhs

        elif self.eq:
            self.cons: C = self.lhs == self.rhs

        elif self.geq:
            self.cons: C = self.lhs >= self.rhs

        else:
            return False

        self._inform()

        # set the constraint
        setattr(
            self.program,
            self.cons_name,
            self.cons,
        )
        # returned for @timer
        return self.sample, self.rel

    def _write_forall(self):
        """Writes the bind constraint for all elements in the set"""

        for n, idx in enumerate(self.forall):

            lhs = self.sample(idx)

            try:
                # if a list is passed
                # or any iterable vector
                rhs = self.parameter[n]
            except TypeError:
                # if not repeat the same value
                # over all elements
                rhs = self.parameter

            if self.leq:
                _ = lhs <= rhs
            if self.geq:
                _ = lhs >= rhs
            if self.eq:
                _ = lhs == rhs

    def _write_w_modes(self):
        """Writes the bind constraint with modes"""

        # create modes
        self.modes = self.model.Modes(size=len(self.parameter), sample=self.sample)

        mode_bounds = [
            (
                (self.parameter[i - 1], self.parameter[i])
                if i - 1 in self.parameter
                else (0, self.parameter[i])
            )
            for i in self.parameter
        ]

        _ = self.sample(self.modes) >= [b[0] for b in mode_bounds]
        _ = self.sample(self.modes) <= [b[1] for b in mode_bounds]

    def _check_existing(self) -> bool:
        """Checks if aspect already has been bound in that space"""
        if (
            self.domain.space in self.aspect.bound_spaces[self.domain.primary][self.rel]
        ) and not self.domain.modes:
            return True

        self.aspect.bound_spaces[self.domain.primary][self.rel].append(
            self.domain.space,
        )

    def _inform(self):
        """Informs the aspect and domain about the bind constraint"""

        # categorize the constraint
        if self.domain.modes:
            self.cons.categorize("Piecewise Linear")
        else:
            self.cons.categorize("Bound")

        # let the aspect know about the new constraint
        self.aspect.constraints.append(self.cons_name)

        # let all objects in the domain know that
        # a constraint with this name contains it
        self.domain.update_cons(self.cons_name)
