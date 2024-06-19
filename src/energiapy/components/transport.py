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
from typing import Dict, Set, List, Union, Tuple

from .material import Material
from .resource import Resource
from .comptype import ResourceType, ParameterType, TransportType, Th
import uuid
from enum import Enum, auto


@dataclass
class Transport:
    """
    Transport moves resource from one location to another

    Args:
        name(str): name of transport, short ones are better to deal with .
        resources(Set[Resource]): specific resources transported through mode.
        material_cons(Dict[Material, float], optional): Materials consumed per unit distance of Transport. Defaults to None.
        introduce(int, optional): when transportation mode is introduced. Defaults to 0.
        retire(int, optional): when transportation mode is retired. Defaults to None
        trans_max(float, optional): maximum capacity of transport that can be set up. Defaults to 0.
        trans_min(float, optional): minimum capacity of transport that needs to be set up. Defaults to 0.
        trans_loss(float, optional): transport losses per unit basis of Raterial per timeperiod in scheduling scale. Defaults to 0.
        emission(float, optional): emissions per unit distance of transportation. Defaults to 0.
        capex(float, optional): capital expenditure on a per unit distance unit capacity basis. Defaults to 0.
        vopex(float, optional): variable operational expenditure on a per unit distance unit capacity basis. Defaults to 0.
        fopex(float, optional): fixed operational expenditure on a per unit distance unit capacity basis. Defaults to 0.
        citation(str, optional): cite data source. Defaults to 'citation needed'.
        label(str, optional): longer descriptive label if required. Defaults to ''.
        varying(List[VaryingTransport], optional): whether any aspect of transport parameters is varying

    Examples:
        Transport objects can be anything from Trains to Pipelines

        >> > Train = Transport(name='Train', resources={H2}, materials_cons={Steel: 100}, trans_max=10000, trans_loss=0.001, capex=300, label= 'Railine for Hydrogen)


    """
    resources: Set[Resource]
    name: str = None
    material_cons: Dict[Material, float] = None
    introduce: int = 0
    retire: int = None
    cap_max: float = None
    cap_min: float = None
    trans_loss: float = None
    emission: float = None
    capex: Union[float, dict, Tuple[float], Th] = None
    vopex: Union[float, dict, Tuple[float], Th] = None
    fopex: Union[float, dict, Tuple[float], Th] = None
    incidental: Union[float, dict, Tuple[float], Th] = None
    citation: str = None
    label: str = None
    ctype: List[TransportType] = None

    def __post_init__(self):

        if self.ctype is None:
            self.ctype = []

        for i in self.resources:
            i.ctype.append(ResourceType.TRANSPORT)
            i.ptype[ResourceType.TRANSPORT] = ParameterType.CERTAIN

        # *-----------------Set ctype---------------------------------
        if self.cap_max is not None:
            self.ctype.append(TransportType.CAPACITY)

        if self.capex is not None:
            self.ctype.append(TransportType.CAPEX)

        if self.fopex is not None:
            self.ctype.append(TransportType.FOPEX)

        if self.vopex is not None:
            self.ctype.append(TransportType.VOPEX)

        if self.incidental is not None:
            self.ctype.append(TransportType.INCIDENTAL)

        # *-----------------Set ptype---------------------------------

        self.ptype = {i: ParameterType.CERTAIN for i in self.ctype}

        if self.cap_max is not None:
            if isinstance(self.cap_max, (tuple, Th)):
                self.ptype[TransportType.CAPACITY] = ParameterType.UNCERTAIN

        if self.capex is not None:
            if isinstance(self.capex, (tuple, Th)):
                self.ptype[TransportType.CAPEX] = ParameterType.UNCERTAIN

        if self.fopex is not None:
            if isinstance(self.fopex, (tuple, Th)):
                self.ptype[TransportType.FOPEX] = ParameterType.UNCERTAIN

        if self.vopex is not None:
            if isinstance(self.vopex, (tuple, Th)):
                self.ptype[TransportType.VOPEX] = ParameterType.UNCERTAIN

        if self.incidental is not None:
            if isinstance(self.incidental, (tuple, Th)):
                self.ptype[TransportType.INCIDENTAL] = ParameterType.UNCERTAIN

        if self.name is None:
            self.name = f"Transport_{uuid.uuid4().hex}"

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
