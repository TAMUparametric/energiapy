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
from typing import Dict, Set, List

from ..components.material import Material
from ..components.resource import Resource

from enum import Enum, auto


class VaryingTransport(Enum):
    """whether the Transport capacity and costs are varying or certain
    """
    DETERMINISTIC_CAPACITY = auto()
    """
    Utilize deterministic data as parameters for capacity
    """
    CERTAIN_CAPACITY = auto()
    """
    Use certain parameter for capacity
    """
    UNCERTAIN_CAPACITY = auto()
    """
    Use uncertain parameter for capacity
    """
    DETERMINISTIC_CAPEX = auto()
    """
    Utilize deterministic data as parameters for capex
    """
    CERTAIN_CAPEX = auto()
    """
    Use certain parameter for capex
    """
    UNCERTAIN_CAPEX = auto()
    """
    Use uncertain parameter for capex
    """
    DETERMINISTIC_VOPEX = auto()
    """
    Utilize deterministic data as parameters for vopex
    """
    CERTAIN_VOPEX = auto()
    """
    Use certain parameter for vopex
    """
    UNCERTAIN_VOPEX = auto()
    """
    Use uncertain parameter for vopex
    """
    DETERMINISTIC_FOPEX = auto()
    """
    Utilize deterministic data as parameters for fopex
    """
    CERTAIN_FOPEX = auto()
    """
    Use certain parameter for fopex
    """
    UNCERTAIN_FOPEX = auto()
    """
    Use uncertain parameter for fopex
    """


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
        trans_max (float, optional): maximum capacity of transport that can be set up. Defaults to 0.
        trans_min (float, optional): minimum capacity of transport that needs to be set up. Defaults to 0.
        trans_loss (float, optional): transport losses per unit basis of Raterial per timeperiod in scheduling scale. Defaults to 0.
        emission (float, optional): emissions per unit distance of transportation. Defaults to 0.
        capex (float, optional): capital expenditure on a per unit distance unit capacity basis. Defaults to 0.
        vopex (float, optional): variable operational expenditure on a per unit distance unit capacity basis. Defaults to 0.
        fopex (float, optional): fixed operational expenditure on a per unit distance unit capacity basis. Defaults to 0.
        citation (str, optional): cite data source. Defaults to 'citation needed'.
        label (str, optional): longer descriptive label if required. Defaults to ''.
        varying(List[VaryingTransport], optional): whether any aspect of transport parameters is varying 

    Examples:
        Transport objects can be anything from Trains to Pipelines

        >>> Train = Transport(name= 'Train', resources= {H2}, materials_cons = {Steel: 100}, trans_max= 10000, trans_loss= 0.001, capex= 300, label = 'Railine for Hydrogen)


    """
    name: str
    resources: Set[Resource]
    material_cons: Dict[Material, float] = None
    introduce: int = 0
    retire: int = None
    trans_max: float = 0
    trans_min: float = 0
    trans_loss: float = 0
    emission: float = 0
    capex: float = 0
    vopex: float = 0
    fopex: float = 0
    citation: str = 'citation needed'
    label: str = ''
    varying: List[VaryingTransport] = None

    def __post_init__(self):
        if self.varying is None:
            self.varying = []

        if (VaryingTransport.DETERMINISTIC_CAPACITY not in self.varying) and (VaryingTransport.UNCERTAIN_CAPACITY not in self.varying):
            self.varying = self.varying + [VaryingTransport.CERTAIN_CAPACITY]

        if (VaryingTransport.DETERMINISTIC_CAPEX not in self.varying) and (VaryingTransport.UNCERTAIN_CAPEX not in self.varying):
            self.varying = self.varying + [VaryingTransport.CERTAIN_CAPEX]

        if (VaryingTransport.DETERMINISTIC_FOPEX not in self.varying) and (VaryingTransport.UNCERTAIN_FOPEX not in self.varying):
            self.varying = self.varying + [VaryingTransport.CERTAIN_FOPEX]

        if (VaryingTransport.DETERMINISTIC_VOPEX not in self.varying) and (VaryingTransport.UNCERTAIN_VOPEX not in self.varying):
            self.varying = self.varying + [VaryingTransport.CERTAIN_VOPEX]

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
