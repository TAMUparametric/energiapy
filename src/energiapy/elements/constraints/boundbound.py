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
    """Bound Constraint that binds with Bound to another Bound

    Attributes:
        root (IsCmp): Root Component for which information is being defined
        attr (str): Attribute of the Component
        varsym (str): Symbol of the Variable
        prmsym (str): Symbol of the Parameter
        parent (Bound): Variable that Bounds this Bound
    """

    parent: Bound = field(default=None)

    def __post_init__(self):

        if not self.varsym:
            self.varsym = self.attr

        if not self.prmsym:
            self.prmsym = f'{self.attr.capitalize()}^f'

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
