"""Rule, to generate Program Constraints
"""

from dataclasses import dataclass, field

from ..core._handy._dunders import _Dunders
from ..core.isalias.elms.iscns import IsCns
from ..core.isalias.elms.isprm import IsPrm
from ..core.isalias.elms.isvar import IsVar
from ..core.nirop.errors import CacodcarError


@dataclass
class Rule(_Dunders):
    """Rule for Constraint generation

    Attributes:
        constraint (IsConstraint): The Constraint to apply
        variable (IsVariable): The main Variable in the Rule
        parameter (IsParameter): The associated Parameter of the Variable
        balance (Dict[IsVariable, float]): Variables to balance at some spatio temporal disposition
        sumover (SumOver): Sum over either a Spatial or Temporal dimension
    """

    constraint: IsCns = field(default=None)
    variable: IsVar = field(default=None)
    parameter: IsPrm = field(default=None)
    balance: dict[IsVar, int] = field(default=None)

    def __post_init__(self):

        if not any([self.variable.parent(), self.parameter]):
            raise CacodcarError(
                'Rule must have at least one of parent (variable) or parameter'
            )
        variable, parent, parameter = ('' for _ in range(3))

        if self.variable:
            variable = f'var:{self.variable.id()}|'
        if self.variable.parent():
            parent = f'pvar:{self.variable.parent().id()}|'
        if self.parameter:
            parameter = f'Param:{self.parameter.id}|'

        self.name = f'{self.constraint.id()}|{variable}{parent}{parameter}'
