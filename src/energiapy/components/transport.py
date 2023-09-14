"""Transport data class
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
from typing import Dict, Set

from ..components.material import Material
from ..components.resource import Resource


@dataclass
class Transport:
    """
    Transport moves resource from one location to another

    Args:
        name (str): name of transport, short ones are better to deal with.
        resources (Set[Resource]): specific resources transported through mode.
        material_cons (Dict[Material, float], optional): Materials consumed per unit distance of Transport. Defaults to None.
        introduce (int, optional): when transportation mode is introduced. Defaults to 0.
        retire (int, optional): when transportation mode is retired. Defaults to None
        trans_max (float, optional): maximum capacity of material that can be transported. Defaults to 0.
        trans_loss (float, optional): transport losses per unit basis of Raterial per timeperiod in scheduling scale. Defaults to 0.
        trans_cost (float, optional): cost per unit distance per unit basis of Resource. Defaults to 0.
        trans_emit (float, optional): carbon emissions per unit distance per unit basis of Resource. Defaults to 0.
        citation (str, optional): cite data source. Defaults to 'citation needed'.
        label (str, optional): Longer descriptive label if required. Defaults to ''.

    Examples:
        Transport objects can be anything from Trains to Pipelines

        >>> Train = Transport(name= 'Train', resources= {H2}, materials_cons = {Steel: 100}, trans_max= 10000, trans_loss= 0.001, trans_cost= 0.002, label = 'Railine for Hydrogen)


    """
    name: str
    resources: Set[Resource]
    material_cons: Dict[Material, float] = None
    introduce: int = 0
    retire: int = None
    trans_max: float = 0
    trans_loss: float = 0
    trans_cost: float = 0
    trans_emit: float = 0
    trans_capex: float = 0
    citation: str = 'citation needed'
    label: str = ''

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name




