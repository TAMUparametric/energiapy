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


@dataclass
class Calculate(_Constraint):
    """Calculate Constraint calculates


    Attributes:
        var (IsVar): Task Variable
    """

    parent: Bound = field(default=None)
    friend: Bound = field(default=None)

    def __post_init__(self):
        setattr(self, 'prmsym', f'{self.friend.prmsym}^{self.parent.varsym}')
        setattr(self, 'varsym', f'{self.friend.varsym}^{self.parent.varsym}')

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
