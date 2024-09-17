"""Adds temporal lag to an event 
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ...core.isalias.cmps.isdfn import IsDfn
from ..parameters.exactprm import ExactPrm
from ..variables.exactvar import ExactVar
from ._constraint import _Constraint
from .rules.delay import Delay

if TYPE_CHECKING:
    from .bound import Bound


@dataclass
class Lag(_Constraint):
    """Adds lag"""

    root: IsDfn = field(default=None)
    parent: Bound = field(default=None)

    def __post_init__(self):
        _Constraint.__post_init__(self)

        self.at = self.parent.root

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

    @property
    def varsym(self):
        """Symbol of the Variable"""
        return f'{self.parent.varsym}^lag'

    @property
    def prmsym(self):
        """Symbol of the Parameter"""
        return f'τ^{self.parent.varsym}'
