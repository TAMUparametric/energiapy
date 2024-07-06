"""Parametric variable 
"""
from dataclasses import dataclass
from typing import List, Optional, Union
from warnings import warn
from .type.disposition import *
from .type.aspect import *
from .type.special import SpecialParameter
from .type.variability import *


@dataclass
class Theta:
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
    aspect: Union[Limit, CashFlow, Land, Emission, Life, Loss] = None
    component: Union['Resource', 'Process', 'Location',
                     'Transport', 'Network', 'Scenario'] = None
    temporal: TemporalDisp = None
    declared_at: Union['Process', 'Location',
                       'Transport', 'Network', 'Scenario'] = None

    def __post_init__(self):

        self.special = SpecialParameter.MPVAR

        if len(self.bounds) != 2:
            warn('bounds need be a tuple of length 2, e.g. (0, 29)')

        if self.bounds is None:
            self.bounds = (0, 1)

        comp, dec_at, par, temp = ('' for _ in range(4))

        if self.aspect:

            if self.declared_at.class_name() in ['Process', 'Location', 'Linkage']:
                if self.declared_at.class_name() != self.component.class_name():
                    self.spatial = (getattr(SpatialDisp, self.component.class_name(
                    ).upper()), getattr(SpatialDisp, self.declared_at.class_name().upper()))
                else:
                    self.spatial = getattr(
                        SpatialDisp, self.declared_at.class_name().upper())
            else:
                self.spatial = SpatialDisp.NETWORK

            self.disposition = ((self.spatial), self.temporal)

            par = f'{self.aspect.name.lower().capitalize()}'
            comp = f'{self.component.name}'
            dec_at = f'{self.declared_at.name}'
            temp = f'{self.temporal.name.lower()}'

            self.index = tuple(dict.fromkeys([comp, dec_at, temp]).keys())
            self.name = f'Th_{par}{self.index}]'

        else:
            self.name = f'Th{self.bounds}'

    #  *----------------- Class Methods ---------------------------------------------

    @classmethod
    def class_name(cls) -> List[str]:
        """Returns class name 
        """
        return cls.__name__

    #  *----------------- Hashing ---------------------------------------------

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name


def birth_theta(value: Union[Theta, tuple], component: Union['Resource', 'Process', 'Location', 'Transport', 'Network', 'Scenario'] = None,
                declared_at: Union['Process', 'Location',
                                   'Transport', 'Network', 'Scenario'] = None,
                aspect: Union[Limit, CashFlow, Land, Emission, Life, Loss] = None, spatial: SpatialDisp = None, temporal: TemporalDisp = None) -> Theta:
    """Creates a parametric variable

    Args:
        value (Union[Theta, tuple]): _description_
        component (Union[energiapy.components]): components such Resource, Process, Location, Transport, Network, Scenario
        aspect (MPVarType): type of parametric variable. Check energiapy.components.parameters
        location (Location, optional): Location where this is being defined. Defaults to None
    Returns:
        Theta: parametric variable 
    """

    if isinstance(value, Theta):
        bounds = value.bounds
    else:
        bounds = value

    return Theta(bounds=bounds, component=component, aspect=aspect, declared_at=declared_at, temporal=temporal)
