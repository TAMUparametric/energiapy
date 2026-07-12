"""Bind constraint"""

from __future__ import annotations

import logging
from functools import cached_property
from typing import TYPE_CHECKING

from gana import V
from gana.sets.function import F

from ...utils.decorators import timer
from ...utils.math import normalize

logger = logging.getLogger("energia")


if TYPE_CHECKING:
    from gana import P as Param
    from gana.sets.constraint import C

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
            | list[dict[float, float]]
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

        # try:
        #     self.write()

        # except TypeError:
        #     # TODO: not yet implemented
        #     # TODO: this is essentially mode of a mode
        #     # TODO: modes will need to made tuple maybe
        #     if any(isinstance(x, dict) for x in self._parameter):
        #         self._write_w_modes_of_modes()

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

        self._categorize()
        self._inform()

        # set the constraint
        setattr(
            self.program,
            self.cons_name,
            self.cons,
        )
        # returned for @timer
        return self.sample, self.rel

    def _listed(self):
        """Gets the parameter as a list if needed"""
        if not isinstance(self._parameter, list) and self.forall:
            return [self._parameter] * len(self.forall)
        return self._parameter

    def _normalized(self, _parameter):
        """Gets the normalized parameter if needed"""
        if self.norm:
            return normalize(_parameter)
        return _parameter

    def _nominalized(self, _parameter):
        """Gets the nominalized parameter if needed"""
        if self.nominal:
            # if a nominal value for the self.parameter is passed
            # this is essentially the expectation
            # skipping an instance check here
            # if a non iterable is passed, let an error be raised

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
        return _parameter

    @cached_property
    def parameter(
        self,
    ) -> (
        list[float]
        | float
        | dict[float, float]
        | tuple[float, float]
        | list[tuple[float, float]]
    ):
        """Parameter bound of the bind constraint"""

        return self._nominalized(self._normalized(self._listed()))

    @cached_property
    def lhs(self):
        """Left hand side of the bind constraint"""

        # ------Get LHS
        # lhs needs to be determined here
        # because V will be spaced and timed if not passed by user
        # .X(), .Vb() need time and space
        return self.sample.V(self.parameter)

    def _rhs_w_bound(self) -> V | F:
        """When the rhs is bound by a variable"""
        _bound = self.sample.X(self.parameter) if self.report else self.sample.Vb()
        return self.parameter * _bound

    def _rhs_w_binary(self) -> V | F:
        """When the rhs is bound by a binary variable"""
        _bound = self.parameter * self.sample.X(self.parameter)
        self.aspect.update(self.domain, reporting=True)
        return _bound

    def _handle_multiplier(self):
        """Gets the parameter with multiplier if needed"""
        if isinstance(self.parameter, list):
            return [p * self.domain.space.multiplier for p in self.parameter]

        return self.parameter * self.domain.space.multiplier

    def _rhs_w_multiplier(self) -> V | F | Param:
        """When the rhs is bound by a multiplier"""
        if self.aspect.use_multiplier:
            _bound = self._handle_multiplier()
        else:
            _bound = self.parameter

        return _bound * self.of(*self.domain.index_spatiotemporal).V(self.parameter)

    @property
    def rhs(self) -> V | F | Param:
        """Right hand side of the bind constraint"""
        if self.of:
            return self._rhs_w_multiplier()

        if self.aspect.bound:
            return self._rhs_w_bound()

        if self.report or self.domain.modes is not None:
            return self._rhs_w_binary()

        return self.parameter

    @cached_property
    def rel(self):
        """Constraint name suffix"""
        if self.leq:
            return "ub"
        elif self.geq:
            return "lb"
        # equality
        if self.iscalc:
            return "inc_calc" if self.report else "calc"
        return "eq"

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

            lhs, rhs = self.sample(idx), self.parameter[n]

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

    # def _write_w_modes_of_modes(self):
    #     """Writes the bind constraint with modes of modes"""
    #     # Consider something like this:
    #     # m.USD.spend(m.PV.capacity, m.PV.construction.modes) == [
    #     #     {100: 1000, 500: 900, 1000: 800},
    #     #     {100: 2000, 500: 1800, 1000: 1600},
    #     #     {100: 3000, 500: 2700, 1000: 2400},
    #     # ]
    #     # I don't want to run a check for this every time, so just catch the error
    #     if self.domain.modes is not None:
    #         for n, p in enumerate(self._parameter):
    #             s = self.sample.aspect(
    #                 *self.domain.edit({'modes': self.domain.modes[n]})
    #             )

    #             if self.leq:
    #                 _ = s <= p
    #             elif self.geq:
    #                 _ = s >= p
    #             elif self.eq:
    #                 _ = s == p

    def _check_existing(self) -> bool:
        """Checks if aspect already has been bound in that space"""
        if not self.iscalc and not self.domain.modes:
            try:
                if self.model.scenario[self.aspect][self.domain.primary][
                    self.domain.space
                ][self.domain.time][self.rel]:
                    return True

            except KeyError:
                pass

        return False

    def _categorize(self):
        """Categorizes the constraint"""
        # categorize the constraint
        if self.iscalc:
            self.cons.categorize("Calculations")
        elif self.domain.modes:
            self.cons.categorize("Piecewise Linear")
        else:
            self.cons.categorize("Binds")

    def _inform(self):
        """Informs the aspect and domain about the bind constraint"""

        # let the aspect know about the new constraint
        self.aspect.constraints.add(self.cons_name)

        # let all objects in the domain know that
        # a constraint with this name contains it
        self.domain.inform_components_of_cons(self.cons_name)

        self.model.scenario.update(self.sample, self.rel, self.P)

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

    @property
    def P(self):
        """Gets the parameter set"""
        if isinstance(self.cons.two, F):
            return self.cons.two.one
        if isinstance(self.cons.two, V):
            return 1.0
        return self.cons.two
