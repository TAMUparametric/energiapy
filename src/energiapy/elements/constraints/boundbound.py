"""Binds a variable to another Bound
"""

from dataclasses import dataclass, field

from ..variables.boundboundvar import BoundBoundVar
from ._constraint import _Constraint
from .bound import Bound
from ..parameters.boundboundprm import BoundBoundPrm
from .rules.bind import Bind


@dataclass
class BoundBound(_Constraint):
    """Bound Constraint that binds with Bound to another Bound"""

    parent: Bound = field(default=None)

    def __post_init__(self):
        setattr(self, 'varsym', self.attr)
        setattr(self, 'prmsym', f'{self.attr.capitalize()}^f')

    @staticmethod
    def var():
        """Variable attributes"""
        return BoundBoundVar

    @staticmethod
    def prm():
        """Parameter"""
        return BoundBoundPrm

    @staticmethod
    def rule():
        """Constraint Rule"""
        return Bind

    @property
    def varbirth_attrs(self):
        """Attributes of the Variable"""
        return {'symbol': self.varsym}
