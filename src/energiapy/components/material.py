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
from typing import Dict

from ..components.resource import Resource


@dataclass
class Material:
    """
    Materials are needed to set up processes. They could result in the emission, toxicty, etc.

    Args:
        name (str): name of the material, short ones are better to deal with
        resource_cons (Dict[Resource, float], optional): Resources consumed per unit basis of Material. Defaults to 0.
        basis (str, optional): Unit basis for material. Defaults to 'unit.
        gwp (float, optional): global warming potential per unit basis of Material produced. Defaults to 0.
        toxicity (float, optional): toxicity potential per unit basis of Material produced. Defaults to 0.
        citation (str, optional): Add citation. Defaults to 'citation needed'.
        label (str, optional): Longer descriptive label if required. Defaults to ''

    Examples:
        Materials can be declared using the resources they consume 

        >>>  Steel = Material(name='Steel', gwp=0.8, resource_cons = {H2O: 3.94}, toxicity=40, basis= 'kg', label='Steel')

    """

    name: str
    resource_cons: Dict[Resource, float] = None
    gwp: float = None
    toxicity: float = None
    basis: str = 'unit'
    citation: str = 'citation needed'
    label: str = ''

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
