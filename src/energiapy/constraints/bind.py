"""Constraint to Bind variable to a lower or upper Parameter or Variable (or both) Bound
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ._constraint import _Constraint
from ..indices.enums import VarBnd

if TYPE_CHECKING:
    from ..core.aliases.is_element import IsParameter, IsVariable


@dataclass
class Bind(_Constraint):
    """Bind variable to another variable or parameter"""

    varbnd: VarBnd = field(default=None)
    parent: IsVariable = field(default=None)
    parameter: IsParameter = field(default=None)

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
