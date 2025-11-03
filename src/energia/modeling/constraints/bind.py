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
    from gana import P, V
    from gana.sets.constraint import C
    from gana.sets.function import F

    from ..._core._component import _Component
    from ..._core._x import _X
    from ..indices.sample import Sample


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
        self._parameter, self.parameter_name = parameter, parameter_name
        self.leq, self.geq, self.eq = leq, geq, eq
        self.forall = forall

        self._handshake()

        if self.forall:
            # if as set is passed
            # write the constraint 'for all' elements in it
            self._write_forall()
            return

        if isinstance(self._parameter, dict):
            # if a dict is passed, it is assumed to be mode bounds
            if self.iscalc:
                self._calc_w_modes()
            else:
                self._write_w_modes()
            return

        self.write()

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

    @property
    def rhs(self) -> V | F | P:
        """Right hand side of the bind constraint"""
        if self.of:
            # if the dependent variable is not set, creates issues.
            # ------if a calculation is being done
            if self.aspect.use_multiplier:
                if isinstance(self.parameter, list):
                    _parameter = [
                        p * self.domain.space.multiplier for p in self.parameter
                    ]
                else:
                    _parameter = self.parameter * self.domain.space.multiplier
            else:
                _parameter = self.parameter

            return _parameter * self.of(*self.domain.index_spatiotemporal).V(
                self.parameter
            )

        if self.aspect.bound:
            # ------if variable bound
            if self.report:
                # ------if variable bound and reported
                # we do not want a bi-linear term
                return self.parameter * self.sample.X(self.parameter)

            # ------if just variable bound

            return self.parameter * self.sample.Vb()

        if self.report or self.domain.modes is not None:
            # ------if  self.parameter bound and reported or has modes
            # create reporting variable write v <= p*x
            self.aspect.update(self.domain, reporting=True)
            return self.parameter * self.sample.X(self.parameter)

        # ------if just self.parameter bound
        return self.parameter

    @cached_property
    def rel(self):
        """Constraint name suffix"""
        if self.leq:
            return "ub"
        elif self.eq:
            if self.of is not None:
                if self.report:
                    return "inc_calc"
                return "calc"
            return "eq"
        elif self.geq:
            return "lb"

    @cached_property
    def cons_name(self):
        """Constraint name"""
        return rf"{self.aspect.name}{self.domain.idxname}_{self.rel}"

    @property
    def iscalc(self) -> bool:
        """Is this a calculation bind constraint?"""
        return self.of is not None

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

    def _calc_w_modes(self):
        """Write with modes"""
        # if this is a dict, piece wise linear functions are being passed
        # Take the example of expenditure and capacity being modeled
        # sat the input is {(0, 200): 5000, (200, 300): 4000, (300, 400): 3000
        # what this implies is that for the capacity between 0 and 200, the expenditure is 5000
        # for the capacity between 200 and 300, the expenditure is 4000
        # for the capacity between 300 and 400, the expenditure is 3000
        # Modes objects index the bin. Three in this case : 1 - (0,200), 2 - (200,300), 3 - (300,400)
        # We need the following equations:
        # *1. capacity = capacity(bin0) + capacity(bin1) + capacity(bin2)
        # *2. x_capacity = 0*capacity(bin0) + 200*capacity(bin1) + 300*capacity(bin2), where is a reporting binary
        # *3-5. spend(bin0) = 5000*capacity(bin0); spend(bin1) = 4000*capacity(bin1); spend(bin2) = 3000*capacity(bin2)
        # *6. spend = spend(bin0) + spend(bin1) + spend(bin2)
        # this takes care of *1 and *2
        _ = self.of == dict(enumerate(self.parameter))
        # this takes care of *3-*6

        # the new modes object would have just been added to the model
        modes = self.model.modes[-1]

        _ = self.of(modes)[self.sample(modes)] == list(self.parameter.values())

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
        if not self.iscalc:
            if (
                (self.domain.space, self.domain.time)
                in self.aspect.bound_spaces[self.domain.primary][self.rel]
            ) and not self.domain.modes:
                return True

            self.aspect.bound_spaces[self.domain.primary][self.rel].append(
                (self.domain.space, self.domain.time)
            )
        return False

    def _inform(self):
        """Informs the aspect and domain about the bind constraint"""

        # categorize the constraint
        if self.iscalc:
            self.cons.categorize("Calculations")
        elif self.domain.modes:
            self.cons.categorize("Piecewise Linear")
        else:
            self.cons.categorize("Binds")

        # let the aspect know about the new constraint
        if self.cons_name not in self.aspect.constraints:
            self.aspect.constraints.append(self.cons_name)

        # let all objects in the domain know that
        # a constraint with this name contains it
        self.domain.inform_indices(self.cons_name)

        self.model.scenario.update(self.sample, self.rel, self.parameter)

    def _handshake(self):
        """Borrow attributes from sample"""
        # borrowed from Sample
        self.model = self.sample.model
        self.nominal = self.sample.nominal
        self.norm = self.sample.norm
        self.domain = self.sample.domain
        self.aspect = self.sample.aspect
        self.report = self.sample.report
        self.program = self.sample.program
        self.of = self.sample.of
