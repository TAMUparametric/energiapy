"""Constraint to calculate Variable. There is usually a parent Variable associated"""

from dataclasses import dataclass


from ._constraint import _Constraint


@dataclass
class Calculate(_Constraint):
    """Calculates; transactions, emissions, etc."""

    def __post_init__(self):
        _Constraint.__post_init__(self)

        # calculations always have an equality sign
        self.birth_equation(eq='==', par=self.parameter, prn=self.parent)
