"""Bind constraint"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...components.temporal.modes import Modes
from ..variables.sample import Sample

if TYPE_CHECKING:
    from ..._core._component import _Component
    from ..._core._x import _X


class Bind:
    """Bind constraint

    :param sample: The sample variable to bind
    :param bound: The bound value
    :param leq: If True, the sample is constrained to be less than or equal to the bound
    :param geq: If True, the sample is constrained to be greater than or equal to the bound
    :param eq: If True, the sample is constrained to be equal to the bound
    """

    def __init__(
        self,
        sample: Sample,
        parameter: float | list | dict,
        leq: bool = False,
        geq: bool = False,
        eq: bool = False,
        forall: list[_X | _Component] = None,
    ):
        self.sample = sample
        self.parameter = parameter
        self.leq = leq
        self.geq = geq
        self.eq = eq
        self.forall = forall

        self.model = sample.model

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

            _ = self(modes) >= modes_lb

            _ = self(modes) <= modes_ub
            return

        if self.sample.

