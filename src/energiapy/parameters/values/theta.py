"""Parametric variable
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from sympy import IndexedBase

from ...core._handy._dunders import _Magics
from ..defined.approach import Approach, Certainty
from ._value import _Value

if TYPE_CHECKING:
    from ...core.aliases.is_input import IsInput, IsSpace


@dataclass
class Theta(_Value, _Magics):
    """Just a convinient way to declare parametric variables

    Args:
        bounds (tuple, optional): (lower, upper) bound. If not provided, defaults to (0, 1)
        component (energiapy.component, optional): Assigned when used as a parameter value for a component. Defaults to None.
        location (Location, optional): Location at which this is being set. Defaults to None.
        aspect (str, optional): Type of MPVar. Defaults to None.

    Examples:

        Say, the selling price of hydrogen in uncertain and can take a value between 0 to 10 dollars

        The first step would be to declare a Theta

        >>> th_h2 = Theta(bounds = (0, 10))

        or simply,

        >>> th_h2 = Theta((0, 10))

        Then th_h2 can be provided when declaring the Resource Hydrogen

        >>> Hydrogen = Resource(name='H2', discharge = True, sell_cost = th_h2)

        This can be done in one step as:

        >>> Hydrogen = Resource(name='H2', discharge = True, sell_cost = Theta((0, 10)))

        Providing the same Theta to different parameters or different components will create unique parametric variables internally.

        For example:

        Each Theta when provided


    """

    space: IsSpace = field(default=None)

    def __post_init__(self):
        _Value.__post_init__(self)

        self._certainty, self._approach = Certainty.CERTAIN, Approach.PARAMETRIC

        if len(self.space) != 2:
            raise ValueError(f'{self.name}: tuple must be of length 2')

    @property
    def value(self) -> dict:
        """Returns a dictionary of data"""
        return self.space

    @property
    def id(self):
        """Symbol"""
        return IndexedBase(f'θ{self.varbnd.value}')
