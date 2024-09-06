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
    """Bound Task"""

    attr: str = field(default=None)
    parent: Bound = field(default=None)

    def __post_init__(self):
        _Constraint.__post_init__(self)
        self.varsym = self.attr
        self.prmsym = f'{self.attr.capitalize()}^f'
        self.name = f'BoundBound|{self.attr}|'

    @staticmethod
    def var():
        """Variable attributes"""
        return BoundBoundVar

    @staticmethod
    def prm():
        """Parameter"""
        return BoundBoundPrm

    @staticmethod
    def cns():
        """Constraint"""
        return Bind

    def varbirth_attrs(self):
        """Attributes of the Variable"""
        return {'symbol': self.varsym}
