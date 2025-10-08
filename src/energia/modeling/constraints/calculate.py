"""Calculation"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

from ...utils.math import normalize
from ..parameters.value import Value

if TYPE_CHECKING:
    from gana.block.program import Prg
    from gana.sets.constraint import C

    from ..._core._x import _X
    from ...represent.model import Model
    from .bind import Bind


@dataclass
class Calculate:
    """
    Calculate the value of a dependent variable based on the value of another variable.

    Usually used when another variable has a degree of freedom.

    :param calc: Calculated (derivative) variable bound.
    :type calc: Bind
    :param decision: Decision variable bound.
    :type decision: Bind

    :ivar decision: Decision variable bound.
    :vartype decision: Bind
    :ivar calc: Calculated (derivative) variable bound.
    :vartype calc: Bind
    :ivar domain: Domain of the calculated variable.
    :vartype domain: Domain
    :ivar name: Name of the calculated variable.
    :vartype name: str
    :ivar program: Program object to which the variable belongs.
    :vartype program: Prg
    :ivar index: Index set of the calculated variable.
    :vartype index: I
    """

    calculation: Bind
    decision: Bind

    def __post_init__(
        self,
    ):
        self.model = self.calculation.model
        self.domain = self.calculation.domain
        self.name = self.calculation.name
        self.program = self.calculation.program
        self.index = self.calculation.index

        self._forall: list[_X] = []

        # if nominal is provided
        # and multiplied by the nominal value
        self._nominal: float = None
        # the input argument is normalized if True
        self._normalize: bool = False

    def forall(self, index) -> Self:
        """Write the constraint for all indices in the index set"""
        self._forall = index
        return self

    def prep(self, nominal: float = 1, norm: bool = True) -> Self:
        """Nominal value
        Args:
            value (float): Nominal value to multiply with bounds
            norm (bool): If the input argument (bounds) are normalized, defaults to True
        """
        self._nominal = nominal
        self._normalize = norm
        return self

    def __eq__(self, other):

        if isinstance(other, dict):
            # if this is a dict, piece wise linear functions are being passed
            # Take the example of expenditure and capacity being modeled
            # sat the input is {(0, 200): 5000, (200, 300): 4000, (300, 400): 3000
            # what this implies is that for the capacity between 0 and 200, the expenditure is 5000
            # for the capacity between 200 and 300, the expenditure is 4000
            # for the capacity between 300 and 400, the expenditure is 3000
            # Modes objects index the bin. Three in this case : 1 - (0,200), 2 - (200,300), 3 - (300,400)
            # We need the following equations:
            # 1. capacity = capacity(bin0) + capacity(bin1) + capacity(bin2)
            # 2. x_capacity = 0*capacity(bin0) + 200*capacity(bin1) + 300*capacity(bin2), where is a reporting binary
            # 3-5. spend(bin0) = 5000*capacity(bin0); spend(bin1) = 4000*capacity(bin1); spend(bin2) = 3000*capacity(bin2)
            # 6. spend = spend(bin0) + spend(bin1) + spend(bin2)

            # this takes care of 1 and 2
            _ = self.decision == dict(enumerate(other))
            # this takes care of 3-6

            # the new modes object would have just been added to the model
            modes = self.model.modes[-1]

            _ = self.decision(modes)[self.calculation(modes)] == list(other.values())

        else:

            if self._nominal:
                if self._normalize:
                    other = [
                        (
                            (self._nominal * i[0], self._nominal * i[1])
                            if isinstance(i, tuple)
                            else self._nominal * i
                        )
                        for i in normalize(other)
                    ]
                else:
                    other = [
                        (
                            (self._nominal * i[0], self._nominal * i[1])
                            if isinstance(i, tuple)
                            else self._nominal * i
                        )
                        for i in other
                    ]

            if isinstance(other, Value):
                time = other.periods
                other = other.value

            else:
                time = None

            if self.decision.aspect not in self.model.dispositions:
                # if a calculation is given directly, without an explicit bound being set
                _ = self.decision == True

            if self._forall:
                if isinstance(other, list):
                    # if other is a list, iterate over the _forall indices
                    for n, idx in enumerate(self._forall):
                        _ = self(idx) == other[n]
                else:
                    for idx in self._forall:
                        # if other is not a list, just compare with the first element
                        _ = self(idx) == other

            else:
                # the aspect being calculated
                if time:
                    calc: Bind = self.calculation(time)
                else:
                    calc: Bind = self.calculation

                if self.decision.domain.modes:
                    # mode calculations, should map to modes
                    calc = calc(self.decision.domain.modes)

                # the aspect the calculation is dependant on
                decision: Bind = self.decision
                if self.decision.report:
                    # incidental, v_inc_calc = P_inc*x_v
                    v_lhs = calc.Vinc(other)
                    domain = calc.domain
                    v_rhs = decision.X(other)
                    cons_name = (
                        rf"{self.calculation.aspect.name}_inc{domain.idxname}_calc"
                    )

                else:
                    # v_calc = P*v
                    v_lhs = calc.V(other)
                    domain = calc.domain
                    v_rhs = decision.V(other)
                    cons_name = rf"{self.calculation.aspect.name}{domain.idxname}_calc"

                cons: C = v_lhs == other * v_rhs

                # categorize the constraint
                cons.categorize("Calculation")

                setattr(
                    self.program,
                    cons_name,
                    cons,
                )

                calc.aspect.constraints.append(cons_name)
                domain.update_cons(cons_name)

    def __call__(self, *index) -> Self:
        return Calculate(
            calculation=self.calculation(*index),
            decision=self.decision(*index),
        )
