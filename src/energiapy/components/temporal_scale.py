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
class temporal_scale:
    """object with the temporal scales of the problem
    e.g.:
    scales = temporal_scale(discretization_list = [1, 365, 24]).generate_scales()
    Generates three temporal scales with 1, 365, and 24 discretizations respectively
    """
    def __init__(self, discretization_list: list):
        """creates a data class with the discretized temporal scale

        Args:
            discretization_list (list): list of discretization of temporal scale
        """
        self.discretization_list = discretization_list
        self.scale  = self.generate_scales()
        self.name = [i for i in range(len(discretization_list))]
        self.scale_levels = len(discretization_list)
    
    def generate_scales(self) -> dict:
        """generates a dict with the scales of the problem

        Returns:
            dict: dictionary with the scales of the problem
        """
        scales_dict = {i: [j for j in range(self.discretization_list[i])] for i in range(len(self.discretization_list))}
        
        return scales_dict

# %%
