"""Program Constraints 
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .._core._handy._dunders import _Dunders

if TYPE_CHECKING:
    from .._core._aliases._is_element import IsParameter, IsVariable


@dataclass
class _Constraint(_Dunders, ABC):
    """Constraints for Program

    Attributes:
        variable (IsVariable): The main Variable in the constraint
        disposition (IsDisposition): The disposition of the constraint. Determined post initialization.
    """

    variable: IsVariable = field(default=None)

    def __post_init__(self):

        # The disposition of the constraint is the same as the main Variable
        self.disposition = self.variable.disposition
        self.name = f'{self.id()}[{self.variable}]'

    @property
    def equation(self):
        """The equation of the constraint"""
        return self._equation

    @equation.setter
    def equation(self, equation):
        self._equation = equation

    @classmethod
    def id(cls):
        """The id of the task"""
        return cls.__name__

    @staticmethod
    def collection():
        """What collection the element belongs to"""
        return 'constraints'

    def birth_equation(self, eq: str, par: IsParameter, prn: IsVariable):
        """Create the equation for the constraint

        Args:
            var (IsVariable): The main Variable in the constraint
            eq (str): The equality sign. '==', '<=', '>='
            par (IsParameter): The parameter in the constraint
            mlt (str): The multiplication sign
            prn (IsVariable): The parent Variable in the constraint
        """
        # make an ordered dictionary to store the equation
        # Why OrderedDict?, I know man. Good to keep things structured

        # A multiplication sign is needed if both parent and parameter are needed

        eqn = OrderedDict((i, None) for i in ['dsp', 'var', 'eq', 'par', 'mlt', 'prn'])

        # Disposition
        eqn['dsp'] = f'{self.disposition}:'
        # LHS
        eqn['var'] = self.variable.id()
        # Equality
        eqn['eq'] = eq
        # RHS
        if par:
            eqn['par'] = par.value.vid
        if prn:
            eqn['prn'] = prn.id()
        if all([par, prn]):
            eqn['mlt'] = '*'

        # Set the equation property
        setattr(self, 'equation', ''.join([i for i in eqn.values() if i]))
