"""Weights for multiobjective optimization (MOO)
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2023, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "MIT"
__version__ = "2.0.0"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from dataclasses import dataclass
from math import isclose
from warnings import warn


@dataclass
class EmissionWeights:
    """Weights for emission objective 

    Args:
        gwp (float): global warming potential 
        odp (float): ozone depletion potential
        acid (float): acidification potential 
        eutt (float): terrestrial eutrophication potential
        eutf (float): freshwater eutrophication potential
        eutm (float): marine eutrophication potential
    """

    gwp: float
    odp: float
    acid: float
    eutt: float
    eutf: float
    eutm: float

    def __post_init__(self):

        self.total = self.gwp + self.odp + self.acid + self.eutt + self.eutf + self.eutm

        if isclose(self.total, 1, abs_tol=1e-2) is not True:
            warn('Total of weights should be equal to 1, check self.total')
