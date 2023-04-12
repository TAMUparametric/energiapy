"""Bounds to initialize model
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
from ..components.result import Result

@dataclass
class CapacityBounds:
    """Capacity minimum bounds from results, for initialization 
    
    Args:
        result: results to induce capacity bounds on new scenario
    """
    result: Result
    def __post_init__(self):
        self.Cap_P_min = self.result.output['Cap_P']
        self.Cap_S_min = self.result.output['Cap_S']