"""Parametric variable 
"""
from dataclasses import dataclass
from typing import List, Optional, Union
from warnings import warn

from .paramtype import MPVarType


@dataclass
class Theta:
    """Just a convinient way to declare parametric variables

    Args:
        bounds (tuple, optional): (lower, upper) bound. If not provided, defaults to (0, 1)
        component (energiapy.component, optional): Assigned when used as a parameter value for a component. Defaults to None.
        location (Location, optional): Location at which this is being set. Defaults to None.
        ptype (str, optional): Type of MPVar. Defaults to None. 

    Examples:

        Say, the selling price of hydrogen in uncertain and can take a value between 0 to 10 dollars

        The first step would be to declare a Theta

        >>> th_h2 = Theta(bounds = (0, 10))

        or simply, 

        >>> th_h2 = Theta((0, 10))

        Then th_h2 can be provided when declaring the Resource Hydrogen

        >>> Hydrogen = Resource(name='H2', discharge = True, sell_price = th_h2)

        This can be done in one step as:

        >>> Hydrogen = Resource(name='H2', discharge = True, sell_price = Theta((0, 10)))

        Providing the same Theta to different parameters or different components will create unique parametric variables internally.

        For example: 

        Each Theta when provided 


    """
    bounds: tuple = None
    component: Union['Resource', 'Process', 'Location',
                     'Transport', 'Network', 'Scenario'] = None
    location: Optional['Location'] = None
    ptype: MPVarType = None

    def __post_init__(self):

        if len(self.bounds) != 2:
            warn('bounds need be a tuple of length 2, e.g. (0, 29)')

        if self.bounds is None:
            self.bounds = (0, 1)

        if self.ptype:
            if self.location:
                self.name = f'Theta({self.component.name},{self.location.name},{str(self.ptype).lower()})'.replace(
                    'mpvartype.', '').replace(f'{self.component.class_name()}_'.lower(), '')
            else:
                self.name = f'Theta({self.component.name},{str(self.ptype).lower()})'.replace(
                    'mpvartype.', '').replace(f'{self.component.class_name()}_'.lower(), '')
        else:
            self.name = f'{self.class_name()}({self.bounds})'

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




def create_mpvar(value: Union[Theta, tuple], component: Union['Resource', 'Process', 'Location', 'Transport', 'Network', 'Scenario'], ptype: MPVarType, location: str = None) -> Theta:
    """Creates a parametric variable

    Args:
        value (Union[Theta, tuple]): _description_
        component (Union[energiapy.components]): components such Resource, Process, Location, Transport, Network, Scenario
        ptype (MPVarType): type of parametric variable. Check energiapy.components.parameters
        location (Location, optional): Location where this is being defined. Defaults to None
    Returns:
        Theta: parametric variable 
    """

    if isinstance(value, Theta):
        bounds = value.bounds
    else:
        bounds = value

    return Theta(bounds=bounds, component=component, ptype=ptype, location=location)
