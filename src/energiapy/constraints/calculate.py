"""Constraint to calculate Variable. There is usually a parent Variable associated"""

from dataclasses import dataclass

from ._constraint import _Constraint


@dataclass
class Calculate(_Constraint):
    """Calculates; expenses, emissions, etc."""

    def __post_init__(self):
        _Constraint.__post_init__(self)
