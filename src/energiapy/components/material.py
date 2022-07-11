"""Material data class  
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
class material:
    """
    Object with data regarding infrastructure material
    """

    def __init__(self, name: str, basis:str= ' - units', label: str = '', gwp: float = 0):
        """material object parameters

        Args:
            name (str): ID for material 
            basis (str): base unit for calculation
            label (str, optional): name of the material. Defaults to ''.
            gwp (float, optional): global warming potential. Defaults to 0.
        """
        self.name = name
        self.label = label + '[' + self.name + ']'
        self.gwp = gwp
        self.basis = basis

    def __repr__(self):
        return self.name
        #self.label + '[' + self.name + ']' + ' - ' + self.basis  

    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        return self.name == other.name
        