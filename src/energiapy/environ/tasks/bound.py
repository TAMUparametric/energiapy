"""Binds a variable based on the Datum provided 
"""

from dataclasses import dataclass, field
from ._task import _Task
from ...elements.variables.boundvar import BoundVar
from ...elements.variables.boundboundvar import BoundBoundVar
from ...elements.constraints.bind import Bind
from ...elements.parameters.boundprm import BoundPrm


@dataclass
class Bound(_Task):
    """Bound Task"""

    p: bool = field(default=False)
    m: bool = field(default=False)

    def __post_init__(self):
        _Task.__post_init__(self)
        self.name = f'Bound|{self.name}|'
        self.parent = None

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
    def cns():
        """Constraint"""
        return Bind

    def varbirth_attrs(self):
        """Attributes of the Variable"""
        return {'p': self.p, 'm': self.m, 'symbol': self.varsym}


@dataclass
class BoundBound(_Task):
    """Bound Task"""

    parent: Bound = field(default=None)

    def __post_init__(self):
        _Task.__post_init__(self)
        self.name = f'BoundBound|{self.name}|'

    @staticmethod
    def var():
        """Variable attributes"""
        return BoundBoundVar

    @staticmethod
    def prm():
        """Parameter"""
        return BoundPrm

    @staticmethod
    def cns():
        """Constraint"""
        return Bind

    def varbirth_attrs(self):
        """Attributes of the Variable"""
        return {'symbol': self.varsym}
