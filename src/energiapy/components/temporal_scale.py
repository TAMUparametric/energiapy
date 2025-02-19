
"""Temporal scale component
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2023, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "MIT"
__version__ = "1.0.5"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from dataclasses import dataclass
from itertools import product
from typing import Tuple, Union


@dataclass
class TemporalScale:
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
    start_zero: Tuple = None
    end_zero: Tuple = None

    def __post_init__(self):
        """
        Creates a list of discretization, scale dict, and number of scale levels

        Args:
            scale (dict): dictionary with the scales as tuples
            list (list): list of scale levels
            name (str): the discretization list is the name.
            scale_levels (int): levels of the scale.
        """
        self.scale_levels = len(self.discretization_list)
        full_scale = {i: list(range(self.discretization_list[i])) for i in range(self.scale_levels)}
        full_iter_list = list(product(*[full_scale[i] for i in full_scale][:self.scale_levels]))

        start_idx = 0
        end_idx = len(full_iter_list) - 1

        if self.start_zero:
            if len(self.start_zero) != self.scale_levels:
                raise ValueError(f"Incorrect start zero declaration. Expected {self.scale_levels} time values")
            else:
                start_idx = full_iter_list.index(self.start_zero)
        else:
            self.start_zero = full_iter_list[start_idx]

        if self.end_zero:
            if len(self.end_zero) != self.scale_levels:
                raise ValueError(f"Incorrect end zero declaration. Expected {self.scale_levels} time values")
            else:
                end_idx = full_iter_list.index(self.end_zero)
        else:
            self.end_zero = full_iter_list[end_idx]

        iter_list = [full_iter_list[t] for t in range(start_idx, end_idx+1)]

        # self.scale = {i: sorted(set(j[i] for j in iter_list)) for i in range(self.scale_levels)}

        self.scale = {i: list(range(self.discretization_list[i])) for i in range(self.scale_levels)}

        self.list = list(range(len(self.discretization_list)))
        self.name = str(self.list)

    def scale_iter(self, scale_level):
        """Generates a list of tuples as a representation of the scales

        Args:
            scale_level (int): The level of the scale for which to generate.

        Returns:
            List[tuple]: list of tuples with representing the scales
        """

        # return [i for i in list(product(*[self.scale[i] for i in self.scale][:scale_level+1]))
        #         if self.start_zero[:scale_level + 1] <= i <= self.end_zero[:scale_level + 1]]

        return list(product(*[self.scale[i] for i in self.scale][:scale_level+1]))

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

