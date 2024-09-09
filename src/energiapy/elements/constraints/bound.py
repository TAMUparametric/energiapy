"""Binds a variable based on the Datum provided 
"""

from dataclasses import dataclass, field
from typing import Self
from ._constraint import _Constraint
from ..variables.boundvar import BoundVar
from .rules.bind import Bind
from ..parameters.boundprm import BoundPrm


@dataclass
class Bound(_Constraint):
    """Bound Constraint

    Attributes:
        root (IsCmp): Root Component for which information is being defined
        attr (str): Attribute of the Component
        varsym (str): Symbol of the Variable
        prmsym (str): Symbol of the Parameter
        sibling (Bound): Sibling Bound, one will add to the balance, the other will take
    """

    sibling: Self = field(default=None)

    def __post_init__(self):

        # Bounds have no parent, they are bound by parameters only
        self.parent = None

        if self.sibling:
            # if sibling is provided, then the sign is negative
            self.sign = -1
            # set this one as the sibling of the sibling
            self.sibling.sibling = self
        else:
            # if sibling is not provided, then the sign is positive
            self.sign = 1

        if not self.varsym:
            self.varsym = self.attr

        if not self.prmsym:
            self.prmsym = f'{self.attr.capitalize()}'

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
        return {'sign': self.sign, 'symbol': self.varsym}
