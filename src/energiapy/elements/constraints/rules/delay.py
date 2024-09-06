"""Constraint Rule to add temporal lag to an event
"""

from dataclasses import dataclass

from ._rule import _Rule


@dataclass
class Delay(_Rule):
    """Bind variable to another variable or parameter"""

    # def __post_init__(self):
    #     _Rule.__post_init__(self)
    #     # Check the bound and add to name and make equality sign
    #     if self.varbnd == VarBnd.LB:
    #         eq = '>='
    #     if self.varbnd == VarBnd.UB:
    #         eq = '<='
    #     if self.varbnd == VarBnd.EQ:
    #         eq = '=='
    #     # Update the name of the constraint if it is a bound
    #     self.name = f'{self.name}{self.varbnd.value}'

    #     # Create the equation for the constraint
    #     self.birth_equation(eq=eq, par=self.parameter, prn=self.parent)
