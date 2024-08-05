"""Parametric variable 
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from pandas import DataFrame

from ...funcs.update.value import update_bounds
from .bounds import Approach, Certainty, SpcLmt, VarBnd
from .constant import Number
from .dataset import DataSet
from .value import Value

if TYPE_CHECKING:
    from ...type.alias import IsRange


@dataclass
class Theta(Value):
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

    space: IsRange = field(default=None)

    def __post_init__(self):
        Value.__post_init__(self)
        self.name = f'Th{self._id}'

        self._certainty, self._approach, self._varbound = (
            Certainty.UNCERTAIN,
            Approach.PARAMETRIC,
            VarBnd.EXACT,
        )

        if len(self.space) == 2:
            # if DataSet or DataFrame, make local DataSet or else keep numeric values
            low_or_up = {0: SpcLmt.START, 1: SpcLmt.END}

            args = {'name': self.name, 'index': self.index}

            self.space = tuple(
                [
                    (
                        update_bounds(DataSet(data=j, **args), spclimit=low_or_up[i])
                        if isinstance(j, DataFrame)
                        else update_bounds(
                            Number(number=j, **args), spclimit=low_or_up[i]
                        )
                    )
                    for i, j in enumerate(self.space)
                ]
            )
        else:
            raise ValueError(f'{self.name}: tuple must be of length 2')

    @property
    def value(self) -> dict:
        """Returns a dictionary of data"""
        return self.space


Th = Theta(name='Th', space=(0, 1))
