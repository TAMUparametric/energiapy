"""Constraint to calculate Variable. There is usually a parent Variable associated"""

from dataclasses import dataclass

from ._rule import _Rule


@dataclass
class Calculation(_Rule):
    """Calculates; transactions, emissions, etc."""

    def __post_init__(self):
        _Rule.__post_init__(self)

        # calculations always have an equality sign
        self.birth_equation(eq='==', par=self.parameter, prn=self.parent)
