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
import uuid


@dataclass
class Material:
    """
    Materials are needed to set up processes. 

    Args:
        name (str): name of the material, short ones are better to deal with
        gwp (float, optional): global warming potential per unit basis of Material produced. Defaults to None.
        odp (float, optional): ozone depletion potential per unit basis of Material produced. Defaults to None.
        acid (float, optional): acidification potential per unit basis of Material produced. Defaults to None.
        eutt (float, optional): terrestrial eutrophication potential per unit basis of Material produced. Defaults to None.
        eutf (float, optional): fresh water eutrophication potential per unit basis of Material produced. Defaults to None.
        eutm (float, optional): marine eutrophication potential per unit basis of Material produced. Defaults to None.
        basis (str, optional): Unit basis for material. Defaults to None.
        citation (str, optional): Add citation. Defaults to None.
        label (str, optional): Longer descriptive label if required. Defaults to None.
        
    Examples:
        Materials can be declared using the resources they consume

        >>>  Steel = Material(name='Steel', gwp=0.8, basis= 'kg', label='Steel')

    """
    name: str = None
    gwp: float = None
    odp: float = None
    acid: float = None
    eutt: float = None
    eutf: float = None
    eutm: float = None
    basis: str = None
    citation: str = None
    label: str = None

    def __post_init__(self):
        
        # *-----------------Set etype (Emission)---------------------------------

        self.etype = []
        self.emissions = dict()
        for i in ['gwp', 'odp', 'acid', 'eutt', 'eutf', 'eutm']:
            if getattr(self, i) is not None:
                self.etype.append(getattr(EmissionType, i.upper()))
                self.emissions[i] = getattr(self, i)

        if self.name is None:
            warn(f'{self.name}: random name has been set, this can be cumbersome')
            self.name = f"Material_{uuid.uuid4().hex}"

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
