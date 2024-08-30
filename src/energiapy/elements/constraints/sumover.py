"""Constraint to sumover time and space
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..indices.enums import VarBnd
from ._constraint import _Constraint

if TYPE_CHECKING:
    from ..core.aliases.iselm import IsParameter, IsVariable


@dataclass
class SumOver(_Constraint):
    """Bind variable to another variable or parameter"""

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
