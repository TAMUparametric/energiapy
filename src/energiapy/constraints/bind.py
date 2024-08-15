"""Constraint to Bind variable to a lower or upper Parameter or Variable (or both) Bound
"""

from dataclasses import dataclass

from ._constraint import _Constraint


@dataclass
class Bind(_Constraint):
    """Bind variable to another variable or parameter"""

    def __post_init__(self):
        _Constraint.__post_init__(self)

