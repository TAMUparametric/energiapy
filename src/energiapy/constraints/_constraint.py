"""Program Constraints 
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING


from ..core._handy._dunders import _Dunders

if TYPE_CHECKING:
    from ..core.aliases.is_element import IsParameter, IsVariable


@dataclass
class _Constraint(_Dunders):
    """Constraints for Program

    Attributes:
        variable (IsVariable): The main Variable in the constraint
        disposition (IsDisposition): The disposition of the constraint. Determined post initialization.
    """

    variable: IsVariable = field(default=None)

    def __post_init__(self):

        # The disposition of the constraint is the same as the main Variable
        self.disposition = self.variable.disposition
        self.name = str(self.sym)

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
        return IndexedBase(cls.__name__)

    @property
    def sym(self):
        """Symbol"""
        return self.id()[self.disposition.sym]

