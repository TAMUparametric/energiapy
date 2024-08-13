"""Parametric variable
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from pandas import DataFrame

from .._core._handy._dunders import _Magics
from ._data import _Data
from .approach import Approach, Certainty
from .bounds import SpcLmt, VarBnd
from .constant import Constant
from .dataset import DataSet

if TYPE_CHECKING:
    from .._core._aliases._is_input import IsInput, IsSpace


@dataclass
class Theta(_Data, _Magics):
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
        _Data.__post_init__(self)

        # self.name = f'{self.name} in {self.space}'

        if self._varbnd is None:
            self._varbnd = VarBnd.PARAMETRIC

        self._certainty, self._approach = Certainty.CERTAIN, Approach.PARAMETRIC

        if len(self.space) != 2:
            raise ValueError(f'{self.name}: tuple must be of length 2')

    @property
    def value(self) -> dict:
        """Returns a dictionary of data"""
        return self.space

    @staticmethod
    def _id():
        """ID to add to name"""
        return 'Th'

    @staticmethod
    def collection():
        """reports what collection the component belongs to"""
        return 'thetas'


Th = Theta(space=(0, 1))