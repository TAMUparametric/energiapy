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


@dataclass
class transport:
    """creates a transport object for specific material
    """
    def __init__(self, name:str, resources:list, locations:list, year:int = 0, label:str = '', trans_max: float = 0, trans_loss: float = 0, trans_cost: float = 0, trans_emit: float = 0):
        """transport object parameters

        Args:
            name (str): ID for transportation mode
            resources (list): specific resources transported through mode.
            locations (list): locations between which transport mode is setup.
            label (int, optional): year when transportation mode is introduced. Defaults to 0.
            label (str, optional): name for the transportation mode. Defaults to ''.
            trans_max (float, optional): maximum capacity of material that can be transported. Defaults to 0.
            trans_loss (float, optional): _description_. Defaults to 0.
            trans_cost (float, optional): _description_. Defaults to 0.
            trans_emit (float, optional): _description_. Defaults to 0.
        """
        self.name = name
        self.resources = resources
        self.locations = locations
        self.year = year
        self.label = label 
        self.trans_max = trans_max
        self.trans_loss = trans_loss
        self.trans_cost = trans_cost
        self.trans_emit = trans_emit
    
    def __refr__(self):
        return self.name