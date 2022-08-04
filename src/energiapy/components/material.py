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
class Material:
    """
    Object with data regarding infrastructure material

    Args:
        name (str): ID 
        basis (str): base unit for calculation
        label (str, optional): name of the material. Defaults to ''.
        gwp (float, optional): global warming potential. Defaults to 0.
        citation (str, optional): add citation. Defaults to 'citation needed'.
    """
    
    name: str 
    label: str = ''
    gwp: tuple=none
    basis: str = 'unit'
    citation: str = 'citation needed'
    H2O: float=0
    
    #? CHECK
    def __post_init__(self):
        self.label = self.label + '[' + self.name + ']'
        
    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        return self.name == other.name
        