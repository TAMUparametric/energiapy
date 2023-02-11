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

from dataclasses import dataclass, field
from typing import Dict
from ..components.resource import Resource

@dataclass
class Material:
    """
    Materials are needed to set up processes. 
    They could result in the emission, toxicty, etc.

    Args:
        name (str): name of the material, short ones are better to deal with
        basis (str): base unit for calculation
        gwp (float, optional): global warming potential. Defaults to 0.
        toxicity (float, optional): toxicity potential. Defaults to 0.
        citation (str, optional): add citation. Defaults to 'citation needed'.
        H20 (str, optional): water consumed per unit. Defaults to 'citation needed'.
        label (str, optional): Longer descriptive label if required. Defaults to ''

    """
    
    name: str 
    gwp: float = None
    toxicity: float = None
    resource_cons: Dict[Resource, float] = field(default_factory= dict)
    basis: str = 'unit'
    citation: str = 'citation needed'
    label: str = ''

    
    #? CHECK
    def __post_init__(self):
        self.label = self.label + '[' + self.name + ']'
        
    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        return self.name == other.name
        