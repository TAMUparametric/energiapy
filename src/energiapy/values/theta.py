"""Parametric variable
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from pandas import DataFrame

from ._approach import _Approach, _Certainty
from ._bounds import _SpcLmt, _VarBnd
from ._value import _Value
from .constant import Constant
from .dataset import DataSet

if TYPE_CHECKING:
    from .._core._aliases._is_input import IsInput, IsSpace


@dataclass
class Theta(_Value):
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
        self.name = f'Th{self._id}'

        self._certainty, self._approach, self._varbound = (
            _Certainty.UNCERTAIN,
            _Approach.PARAMETRIC,
            _VarBnd.EXACT,
        )

        if len(self.space) == 2:
            # if DataSet or DataFrame, make local DataSet or else keep numeric
            # values
            low_or_up = {0: _SpcLmt.START, 1: _SpcLmt.END}

            args = {'name': self.name, 'disposition': self.disposition}

            self.space = tuple(
                [
                    (
                        self.update_bounds(
                            DataSet(data=j, **args), spclimit=low_or_up[i]
                        )
                        if isinstance(j, DataFrame)
                        else self.update_bounds(
                            Constant(constant=j, **args), spclimit=low_or_up[i]
                        )
                    )
                    for i, j in enumerate(self.space)
                ]
            )
        else:
            raise ValueError(f'{self.name}: tuple must be of length 2')

    def update_bounds(
        self, value: IsInput, varbound: _VarBnd = None, spclimit: _SpcLmt = None
    ):
        """Updates the name to add a variable bound"""
        if varbound:
            setattr(value, '_varbound', varbound)

        if spclimit:
            setattr(value, '_spclimit', spclimit)

    @property
    def value(self) -> dict:
        """Returns a dictionary of data"""
        return self.space


Th = Theta(name='Th', space=(0, 1))
