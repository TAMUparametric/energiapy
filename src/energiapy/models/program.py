from __future__ import annotations

from typing import TYPE_CHECKING

from dataclasses import dataclass, field

if TYPE_CHECKING:
    from ..type.alias import IsVariable, IsConstraint, IsParameter, IsValue

@dataclass
class Program:
    """Mathematical Programming Model

    Args:
        variables (IsVariable): Variables to be used
        constraints (IsConstraint): Constraints to be used
        parameters (IsParameter): Parameters to be used
        values (IsValue): Values to be used
    """
    variables: IsVariable = field(default=None)
    constraints: IsConstraint = field(default=None)
    parameters: IsParameter = field(default=None)
    data: IsData = field(default=None)
