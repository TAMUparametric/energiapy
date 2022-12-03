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

@dataclass
class Temporal_scale:
    """object with the temporal scales of the problem
    e.g.:
    scales = temporal_scale(discretization_list = [1, 365, 24]).generate_scales()
    Generates three temporal scales with 1, 365, and 24 discretizations respectively
    Args:
        discretization_list (list): list of discretization of temporal scale
    """
    discretization_list: list
    start_zero: int = None
    
    def __post_init__(self):        
        self.scale  = {i: [j for j in range(self.discretization_list[i])] for i in range(len(self.discretization_list))}
        self.list = [i for i in range(len(self.discretization_list))]
        self.name = f"{[i for i in range(len(self.list))]}"
        self.scale_levels = len(self.discretization_list)
        
    def __repr__(self):
        return self.name
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        return self.name == other.name

# %%
