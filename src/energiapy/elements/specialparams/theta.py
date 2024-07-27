"""Parametric variable 
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from warnings import warn

from pandas import DataFrame

from ...core.base import Dunders
from ..index import Index
from .dataset import DataSet

if TYPE_CHECKING:
    from ...type.alias import IsAspect, IsComponent, IsDeclaredAt, IsTemporal


@dataclass
class Theta(Dunders):
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
    bounds: tuple = None
    aspect: IsAspect = None
    component: IsComponent = None
    declared_at: IsDeclaredAt = None
    temporal: IsTemporal = None

    def __post_init__(self):

        if len(self.bounds) != 2:
            warn('bounds need be a tuple of length 2, e.g. (0, 29)')

        if self.bounds is None:
            self.bounds = (0, 1)

        if self.aspect:
            self.index = Index(
                component=self.component, declared_at=self.declared_at, temporal=self.temporal)
            self.name = f'Th|{self.aspect.pname().capitalize()}{self.index.name}|'

        else:
            self.name = f'Th{self.bounds}'

    def __len__(self):
        return max([len(i) if isinstance(i, (DataFrame, DataSet)) else 1 for i in self.bounds])
