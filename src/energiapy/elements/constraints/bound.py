"""Binds a variable based on the Datum provided 
"""

from dataclasses import dataclass, field
from typing import Self

from ...core.isalias.cmps.iscmp import IsCmp
from ..parameters.boundprm import BoundPrm
from ..variables.boundvar import BoundVar
from ._constraint import _Constraint
from .rules.bind import Bind


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

    root: IsCmp = field(default=None)
    sibling: Self = field(default=None)

    def __post_init__(self):
        _Constraint.__post_init__(self)
        # Bounds have no parent, they are bound by parameters only
        self.parent = None

        if self.sibling:
            # if sibling is provided, then the sign is negative
            self.sign = -1
            # set this one as the sibling of the sibling
            self.sibling.sibling = self
            # and take the root from there
            self.root = self.sibling.root
        else:
            # if sibling is not provided, then the sign is positive
            self.sign = 1

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

    @property
    def varsym(self):
        """Symbol of the Variable"""
        return self.attr

    @property
    def prmsym(self):
        """Symbol of the Parameter"""
        return f'{self.attr.capitalize()}'
