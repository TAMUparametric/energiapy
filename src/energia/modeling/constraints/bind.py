"""Bind constraint"""

from __future__ import annotations

import logging
import time as keep_time
from typing import TYPE_CHECKING

from ...components.temporal.modes import Modes
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
    ):
        self.sample = sample
        self.parameter = parameter
        self.leq = leq
        self.geq = geq
        self.eq = eq
        self.forall = forall

        self.model = sample.model

        self.nominal = sample.nominal
        self.norm = sample.norm
        self.domain = sample.domain
        self.aspect = sample.aspect
        self.report = sample.report
        self.program = sample.program

        # when i say all elements in the set, it implies that each element features
        # individually in the index of the updated sample

        # if as set is passed
        # write the constraint 'for all' elements in it
        if self.forall:

            if isinstance(parameter, list):
                # if a list is passed
                # iterate over it
                for n, idx in enumerate(self.forall):
                    if self.leq:
                        _ = self.sample(idx) <= parameter[n]
                    if self.geq:
                        _ = self.sample(idx) >= parameter[n]
                    if self.eq:
                        _ = self.sample(idx) == parameter[n]
                return

            # if a single value is passed
            # just repeat the same value over
            # all elements in the set

            for idx in self.forall:

                if self.leq:
                    _ = self.sample(idx) <= parameter
                if self.geq:
                    _ = self.sample(idx) >= parameter
                if self.eq:
                    _ = self.sample(idx) == parameter

            return

        if isinstance(parameter, dict):
            # if a dictionary is passed
            # modes are assumed
            n_modes = len(parameter)
            modes_name = f"bin{len(self.model.modes)}"

            setattr(self.model, modes_name, Modes(n_modes=n_modes, bind=self.sample))

            # this gets the last set mode (which was just set above)
            modes = self.model.modes[-1]
            mode_bounds = [
                (
                    (parameter[i - 1], parameter[i])
                    if i - 1 in parameter
                    else (0, parameter[i])
                )
                for i in parameter
            ]
            modes_lb = [b[0] for b in mode_bounds]
            modes_ub = [b[1] for b in mode_bounds]

            _ = self.sample(modes) >= modes_lb

            _ = self.sample(modes) <= modes_ub
            return

        if self.nominal:
            # if a nominal value for the parameter is passed
            # this is essentially the expectation
            # skipping an instance check here
            # if a non iterable is passed, let an error be raised
            if self.norm:
                parameter = normalize(parameter)

            # if the sample needs to be normalized
            parameter = [
                (
                    (self.nominal * i[0], self.nominal * i[1])
                    if isinstance(i, tuple)
                    else self.nominal * i
                )
                for i in parameter
            ]

            # ------Get LHS
            # lhs needs to be determined here
            # because V will be spaced and timed if not passed by user
            # .X(), .Vb() need time and space

        lhs = self.sample.V(parameter)

        logger.info("Binding %s in domain %s", self.aspect, self.domain)

        start = keep_time.time()
        # ------Get RHS

        if self.aspect.bound is not None:
            # ------if variable bound
            if self.report:
                # ------if variable bound and reported
                # we do not want a bi-linear term
                rhs = parameter * self.sample.X(parameter)

            else:
                # ------if just variable bound
                rhs = parameter * self.sample.Vb()

        elif self.report or self.domain.modes is not None:
            # ------if  parameter bound and reported or has modes
            # create reporting variable write v <= p*x
            rhs = parameter * self.sample.X(parameter)
            self.aspect.update(self.domain, reporting=True)

        else:
            # ------if just parameter bound
            rhs = parameter

        if self.leq:
            # Less than equal to
            if (
                self.domain.space in self.aspect.bound_spaces[self.domain.primary]["ub"]
            ) and not self.domain.modes:
                # return if aspect already bound in space
                return
            self.aspect.bound_spaces[self.domain.primary]["ub"].append(
                self.domain.space,
            )
            cons: C = lhs <= rhs
            rel = "_ub"

        elif self.eq:
            # Exactly equal to
            cons: C = lhs == rhs
            rel = "_eq"

        elif self.geq:
            # Greater than equal to
            if (
                self.domain.space in self.aspect.bound_spaces[self.domain.primary]["lb"]
            ) and not self.domain.modes:
                # return if aspect already bound in space
                return
            self.aspect.bound_spaces[self.domain.primary]["lb"].append(
                self.domain.space,
            )
            cons: C = lhs >= rhs
            rel = "_lb"
        else:
            return

        # name of the constraint
        cons_name = rf"{self.aspect.name}{self.domain.idxname}{rel}"

        # categorize the constraint
        if self.domain.modes:
            cons.categorize("Piecewise Linear")
        else:
            cons.categorize("Bound")

        # let all objects in the domain know that
        # a constraint with this name contains it
        self.domain.update_cons(cons_name)

        # let the aspect know about the new constraint
        self.aspect.constraints.append(cons_name)

        # set the constraint
        setattr(
            self.program,
            cons_name,
            cons,
        )

        end = keep_time.time()
        logger.info("\u2714 Completed in %s seconds", end - start)

