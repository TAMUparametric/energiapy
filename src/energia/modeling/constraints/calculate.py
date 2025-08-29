"""Calculation"""

from __future__ import annotations

from typing import TYPE_CHECKING, Self

from ..parameters.value import Value

if TYPE_CHECKING:
    from gana.block.program import Prg
    from gana.sets.function import F

    from ...core.x import X
    from ...represent.model import Model
    from .bind import Bind


class Calculate:
    """Calculate the value of a dependent variable based on the value of another variable

    Usually, another variable that has a degree of freedom

    Args:
        calc (Bind): Calculated (derivative) Variable bound
        decision (Bind): Decision variable bound

    Attributes:
        decision (Bind): Variable bound
        calc (Bind): Calculated (derivative) Variable bound
        self.domain (Domain): Domain of the calculated variable
        name (str): Name of the calculated variable
        program (Prg): Program object
        index (I): Index set of the calculated variable
    """

    def __init__(
        self,
        calculation: Bind,
        decision: Bind,
    ):
        self.decision = decision
        self.calculation = calculation
        self.domain = calculation.domain
        self.name = calculation.name
        self.program: Prg = decision.program
        self.index = calculation.index
        self._forall: list[X] = []

    @property
    def model(self) -> Model:
        """Model to which the Calc belongs"""
        return self.decision.model

    def forall(self, index) -> Self:
        """Write the constraint for all indices in the index set"""
        self._forall = index
        return self

    def __call__(self, *index) -> Self:
        # update the index and return a Calc object

        _index = list(index) + self.index
        print('aaa', self.index, index)

        return Calculate(
            calculation=self.calculation(*_index), decision=self.decision(*index)
        )

    def __eq__(self, other):

        if isinstance(other, Value):
            time = other.period
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

            # the aspect the calculation is dependant on
            decision: Bind = self.decision
            if self.decision.report:
                # incidental, v_inc_calc = P_inc*x_v
                v_lhs = calc.Vinc(other)
                domain = calc.domain
                v_rhs = decision.X(other)
                cons_name = rf'{self.name}_inc{domain.idxname}_calc'

            else:
                # v_calc = P*v
                v_lhs = calc.V(other)
                domain = calc.domain
                v_rhs = decision.V(other)
                cons_name = rf'{self.name}{domain.idxname}_calc'

            cons: F = v_lhs == other * v_rhs

            # categorize the constraint
            cons.categorize('Calculation')

            setattr(
                self.program,
                cons_name,
                cons,
            )

            calc.aspect.constraints.append(cons_name)
            domain.update_cons(cons_name)


# class Calculate:
#     """Calculate the value of a dependent variable based on the value of another variable

#     Usually, another variable that has a degree of freedom

#     Args:
#         calc (Bind): Calculated (derivative) Variable bound
#         decision (Bind): Decision variable bound

#     Attributes:
#         decision (Bind): Variable bound
#         calc (Bind): Calculated (derivative) Variable bound
#         self.domain (Domain): Domain of the calculated variable
#         name (str): Name of the calculated variable
#         program (Prg): Program object
#         index (I): Index set of the calculated variable
#     """

#     def __init__(
#         self,
#         calc: Bind,
#         decision: Bind,
#     ):
#         self.decision = decision
#         self.domain = calc.domain
#         self.calc = calc(*decision.index)
#         self.name = calc.name
#         self.program: Prg = decision.program
#         self.index = calc.index
#         self._forall: list[X] = []

#     @property
#     def model(self) -> Model:
#         """Model to which the Calc belongs"""
#         return self.decision.model

#     def forall(self, index) -> Self:
#         """Write the constraint for all indices in the index set"""
#         self._forall = index
#         return self

#     def __call__(self, *index) -> Self:
#         # update the index and return a Calc object
#         _index = list(index) + self.index

#         return Calculate(calc=self.calc(*_index), decision=self.decision(*index))

#     def __eq__(self, other):

#         if isinstance(other, Value):
#             time = other.period
#             other = other.value

#         else:
#             time = None

#         if self.decision.aspect not in self.model.dispositions:
#             # if a calculation is given directly, without an explicit bound being set
#             _ = self.decision == True

#         if self._forall:
#             if isinstance(other, list):
#                 # if other is a list, iterate over the _forall indices
#                 for n, idx in enumerate(self._forall):
#                     _ = self(idx) == other[n]
#             else:
#                 for idx in self._forall:
#                     # if other is not a list, just compare with the first element
#                     _ = self(idx) == other

#         else:
#             # the aspect being calculated
#             if time:
#                 calc: Bind = self.calc(self.decision, time)
#             else:
#                 calc: Bind = self.calc(self.decision)

#             # the aspect the calculation is dependant on
#             decision: Bind = self.decision
#             if self.decision.report:
#                 # incidental, v_inc_calc = P_inc*x_v
#                 v_lhs = calc.Vinc(other)
#                 domain = calc.domain
#                 v_rhs = decision.X(other)
#                 cons_name = rf'{self.name}_inc{domain.idxname}_calc'

#             else:
#                 # v_calc = P*v
#                 v_lhs = calc.V(other)
#                 domain = calc.domain
#                 v_rhs = decision.V(other)
#                 cons_name = rf'{self.name}{domain.idxname}_calc'

#             cons: C = v_lhs == other * v_rhs

#             # categorize the constraint
#             cons.categorize('Calculation')

#             setattr(
#                 self.program,
#                 cons_name,
#                 cons,
#             )

#             calc.aspect.constraints.append(cons_name)
#             domain.update_cons(cons_name)
