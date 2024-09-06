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
    """Calculation Task
    Handles the attributes of components
    Defines strict behaviour

    Attributes:
        var (IsVar): Task Variable
    """

    parent: Bound = field(default=None)
    friend: Bound = field(default=None)

    def __post_init__(self):
        _Constraint.__post_init__(self)
        self.prmsym = f'{self.friend.prmsym}^{self.parent.varsym}'
        self.varsym = f'{self.friend.varsym}^{self.parent.varsym}'
        self.attr = f'{self.parent.name}_{self.friend.name}'
        self.name = f'Calculate|{self.attr}|'

    @staticmethod
    def var():
        """Variable"""
        return ExactVar

    @staticmethod
    def prm():
        """Parameter"""
        return ExactPrm

    @staticmethod
    def cns():
        """Constraint"""
        return Calculation

    def varbirth_attrs(self):
        """Attributes of the Variable"""
        return {'symbol': self.varsym}
