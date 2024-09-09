"""Binds a variable based on the Datum provided 
"""

from dataclasses import dataclass, field
from ._constraint import _Constraint
from ..variables.boundvar import BoundVar
from .rules.bind import Bind
from ..parameters.boundprm import BoundPrm


@dataclass
class Bound(_Constraint):
    """Bound Constraint"""

    p: bool = field(default=False)
    m: bool = field(default=False)

    def __post_init__(self):
        self.parent = None
        setattr(self, 'varsym', self.attr)
        setattr(self, 'prmsym', f'{self.attr.capitalize()}')

        if self.p and self.m:
            raise ValueError('Task cannot be both plus and minus')

        if not (self.p or self.m):
            raise ValueError('Task must be either plus or minus')

    @staticmethod
    def var():
        """Variable"""
        return BoundVar

    @staticmethod
    def prm():
        """Parameter"""
        return BoundPrm

    @staticmethod
    def rule():
        """Constraint Rule"""
        return Bind

    @property
    def varbirth_attrs(self):
        """Attributes of the Variable"""
        return {'p': self.p, 'm': self.m, 'symbol': self.varsym}
