"""Binds a variable to another Bound
"""

from dataclasses import dataclass, field

from ...elements.variables.boundboundvar import BoundBoundVar
from ._task import _Task
from .bound import Bound
from ...elements.parameters.boundprm import BoundPrm
from ...elements.constraints.bind import Bind


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
