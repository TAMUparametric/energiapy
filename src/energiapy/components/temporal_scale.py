#%%
"""Temporal scale component
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "0.0.1"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from dataclasses import dataclass
from functools import reduce
import operator
from itertools import product
from typing import List

@dataclass
class Temporal_scale:
    """
    Multiple temporal scales of the problems
    
    Args:
        discretization_list (list): list of discretization of temporal scale
        start_zero (int): which year the scale starts. Defaults to None.

    Examples:
        The following example represents a year and generates three temporal scales with 1, 365, and 24 discretizations respectively.
        
        >>> scales = temporal_scale(discretization_list = [1, 365, 24])
        
        A starting year can be specified
        
        >>> scales = temporal_scale(discretization_list = [1, 365, 24], start_zero= 1993)

    """
    discretization_list: list
    start_zero: int = None
    
    def __post_init__(self):     
        """
        Creates a list of discretization, scale dict, and number of scale levels
        
        Args:
            scale (dict): dictionary with the scales as tuples
            list (list): list of scale levels
            name (str): the discretization list is the name.
            scale_levels (int): levels of the scale.
        """   
        self.scale  = {i: [j for j in range(self.discretization_list[i])] for i in range(len(self.discretization_list))}
        self.list = [i for i in range(len(self.discretization_list))]
        self.name = f"{[i for i in range(len(self.list))]}"
        self.scale_levels = len(self.discretization_list)
        
    def scale_iter(self, scale_level):
        """Generates a list of tuples as a representation of the scales

        Args:
            scale_level (int): The level of the scale for which to generate.

        Returns:
            List[tuple]: list of tuples with representing the scales 
        """
        return [(i) for i in product(*[self.scale[i] for i in self.scale][:scale_level+1])]
        
    def __repr__(self):
        return self.name
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        return self.name == other.name

# %%
