"""Transport data class  
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
from typing import Set
from ..components.resource import Resource

@dataclass
class Transport:
    """creates a transport object for specific material
        Args:
        name (str): ID for transportation mode
        resources (Set[Resource]): specific resources transported through mode.
        intro_scale (int, optional): when transportation mode is introduced. Defaults to 0.
        label (str, optional): name for the transportation mode. Defaults to ''.
        trans_max (float, optional): maximum capacity of material that can be transported. Defaults to 0.
        trans_loss (float, optional): transport lossed per unit of scheduling scale. Defaults to 0.
        trans_cost (float, optional): cost per unit distance. Defaults to 0.
        trans_emit (float, optional): carbon emissions per unit distance. Defaults to 0.
        citation (str, optional): cite data source. Defaults to citation needed
    """
    name: str
    resources: Set[Resource]
    intro_scale: int = 0
    label: str = '' 
    trans_max: float = 0
    trans_loss: float = 0
    trans_cost: float = 0
    trans_emit: float = 0
    citation: str = 'citation needed'

    def __refr__(self):
        return self.name
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        return self.name == other.name
