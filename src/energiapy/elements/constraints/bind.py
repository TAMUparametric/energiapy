"""Constraint to Bind variable to a lower or upper Parameter or Variable (or both) Bound
"""

from dataclasses import dataclass, field

from ...core.isalias.elms.isprm import IsPrm
from ...core.isalias.elms.isvar import IsVar
from ..disposition.bound import VarBnd
from ._constraint import _Constraint


@dataclass
class Bind(_Constraint):
    """Bind variable to another variable or parameter"""

    varbnd: VarBnd = field(default=None)
    parent: IsVar = field(default=None)
    parameter: IsPrm = field(default=None)

    def __post_init__(self):
        _Constraint.__post_init__(self)
        # Check the bound and add to name and make equality sign
        if self.varbnd == VarBnd.LB:
            eq = '>='
        if self.varbnd == VarBnd.UB:
            eq = '<='
        if self.varbnd == VarBnd.EQ:
            eq = '=='
        # Update the name of the constraint if it is a bound
        self.name = f'{self.name}{self.varbnd.value}'

        # Create the equation for the constraint
        self.birth_equation(eq=eq, par=self.parameter, prn=self.parent)
