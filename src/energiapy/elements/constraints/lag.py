"""Adds temporal lag to an event 
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from dataclasses import dataclass, field
from ._constraint import _Constraint
from ..variables.exactvar import ExactVar
from .rules.delay import Delay
from ..parameters.exactprm import ExactPrm

if TYPE_CHECKING:
    from .bound import Bound


@dataclass
class Lag(_Constraint):
    """Adds lag"""

    parent: Bound = field(default=None)

    def __post_init__(self):
        setattr(self, 'prmsym', f'τ^{self.parent.varsym}')
        setattr(self, 'varsym', f'{self.parent.varsym}^lag')

        if not self.attr:
            self.attr = f'{self.parent.name}_time'

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
        """Constraint"""
        return Delay

    @property
    def varbirth_attrs(self):
        """Attributes of the Variable"""
        return {'symbol': self.varsym}
