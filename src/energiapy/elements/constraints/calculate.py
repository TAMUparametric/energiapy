"""Calculates the value of a Variable based on the Parent Task
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from dataclasses import dataclass, field
from ._constraint import _Constraint
from ..variables.exactvar import ExactVar
from .rules.calculation import Calculation
from ..parameters.exactprm import ExactPrm

if TYPE_CHECKING:
    from .bound import Bound
    from .boundbound import BoundBound


@dataclass
class Calculate(_Constraint):
    """Calculate Constraint calculates


    Attributes:
        root (IsCmp): Root Component for which information is being defined
        attr (str): Attribute of the Component
        varsym (str): Symbol of the Variable
        prmsym (str): Symbol of the Parameter
        parent (Bound): Bound gives the value to calculate
        friend (Bound): This calculation contributes to this Bound
    """

    parent: Bound | BoundBound = field(default=None)
    friend: Bound | BoundBound = field(default=None)

    def __post_init__(self):

        if not self.varsym:
            self.prmsym = f'{self.friend.prmsym}^{self.parent.varsym}'
            self.varsym = f'{self.friend.varsym}^{self.parent.varsym}'

        if not self.attr:
            self.attr = f'{self.parent.name}_{self.friend.name}'

    @staticmethod
    def var():
        """Variable"""
        return ExactVar

    @staticmethod
    def prm():
        """Parameter"""
        return ExactPrm

    @staticmethod
    def rule():
        """Constraint Rule"""
        return Calculation

    @property
    def varbirth_attrs(self):
        """Attributes of the Variable"""
        return {'symbol': self.varsym}
