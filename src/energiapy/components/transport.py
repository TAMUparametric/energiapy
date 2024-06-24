"""energiapy.Transport - moves Resources between Locations
"""
# TODO ---- apply material constraints
# TODO --- trans_loss, retire, introduce, land, land_cost (could be between location.. will need to check)


import uuid
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple, Union

from .comptype import EmissionType, ResourceType, TransportType
from .location import Location
from .material import Material
from .parameters.mpvar import Theta, create_mpvar
from .parameters.paratype import FactorType, MPVarType, ParameterType
from .resource import Resource


@dataclass
class Transport:
    """
    Transports move Resource from one Location to Another 

    Args:
        name(str): name of transport, short ones are better to deal with .
        resources(Set[Resource]): specific resources transported through mode.
        material_cons(Dict[Material, float], optional): Materials consumed per unit distance of Transport. Defaults to None.
        cap_max(float, optional): maximum capacity that can be set up. Defaults to None.
        cap_min(float, optional): minimum capacity required to set up. Defaults to None.
        trans_loss(float, optional): transport losses per unit basis of Resource for timeperiod in scheduling scale. Defaults to 0.
        capex(float, optional): capital expenditure on a per unit distance unit capacity basis. Defaults to None.
        vopex(float, optional): variable operational expenditure on a per unit distance unit capacity basis. Defaults to None.
        fopex(float, optional): fixed operational expenditure on a per unit distance unit capacity basis. Defaults to None.
        incidental(float, optional): incidental expenditure on a per unit distance unit capacity basis. Defaults to None.
        gwp (float, optional): global warming potential for settting up transportation per unit distance. Defaults to None.
        odp (float, optional): ozone depletion potential for settting up transportation per unit distance. Defaults to None.
        acid (float, optional): acidification potential for settting up transportation per unit distance. Defaults to None.
        eutt (float, optional): terrestrial eutrophication potential for settting up transportation per unit distance. Defaults to None.
        eutf (float, optional): fresh water eutrophication potential for settting up transportation per unit distance. Defaults to None.
        eutm (float, optional): marine eutrophication potential for settting up transportation per unit distance. Defaults to None.
        introduce(int, optional): when transportation mode is introduced. Defaults to None.
        retire(int, optional): when transportation mode is retired. Defaults to None.
        basis (str, optional): unit for measuring cost and distance. Defaults to None .
        block (Union[str, list, dict], optional): block to which it belong. Convinient to set up integer cuts. Defaults to None.
        label (str, optional): used while generating plots. Defaults to None.
        citation (str, optional): can provide citations for your data sources. Defaults to None.
        ctype (List[LandType], optional): Transport type. Defaults to None.
        ptype (Dict[LandType, ParameterType], optional): paramater type of declared values. Defaults to None.
        ftype (Dict[TransportType, Tuple[Tuple[Location, Location], FactorType]], optional): factor type of declared factors. Defaults to None. 

    Examples:

        Transport objects can be anything from Trains to Pipelines

        >>> Train = Transport(name='Train', resources={H2}, materials_cons={Steel: 100}, trans_max=10000, trans_loss=0.001, capex=300, label= 'Railine for Hydrogen)

    """

    name: str
    # Primary attributes
    resources: Set[Resource]
    material_cons: Dict[Material, float] = None
    # Design Parameters
    cap_max: float = None
    cap_min: float = None
    trans_loss: float = None
    # Expenditure
    capex: Union[float, dict, Tuple[float], Theta] = None
    vopex: Union[float, dict, Tuple[float], Theta] = None
    fopex: Union[float, dict, Tuple[float], Theta] = None
    incidental: Union[float, dict, Tuple[float], Theta] = None
    # Emissions
    gwp: float = None
    odp: float = None
    acid: float = None
    eutt: float = None
    eutf: float = None
    eutm: float = None
    # Temporal
    introduce: int = 0
    retire: int = None
    # Details
    basis: str = None
    block: str = None
    label: str = None
    citation: str = None
    # Type
    ctype: List[TransportType] = None
    ptype: Dict[TransportType, ParameterType] = None
    ftype: Dict[TransportType,
                Tuple[Tuple[Location, Location], FactorType]] = None
    # Depricated
    trans_max: float = None
    trans_min: float = None
    emission: float = None
    varying: bool = None

    def __post_init__(self):

        # *-----------------Set ctype---------------------------------
        if self.ctype is None:
            self.ctype = []

        for i in self.resources:  # update Resource if transported
            i.ctype.append(ResourceType.TRANSPORT)
            i.ptype[ResourceType.TRANSPORT] = ParameterType.CERTAIN

        if self.cap_max is not None:
            self.ctype.append(TransportType.CAPACITY)

        for i in ['cap_max', 'cap_min', 'capex', 'fopex', 'vopex', 'incidental']:
            if getattr(self, i) is not None:
                self.ctype.append(getattr(TransportType, i.upper()))

        # *-----------------Set ptype---------------------------------
        # If parameter provided as Theta or tuple bounds are provided - makes MPVar

        self.ptype = {i: ParameterType.CERTAIN for i in self.ctype}

        for i in ['cap_max', 'capex', 'fopex', 'vopex', 'incidental']:
            if getattr(self, i) is not None:
                if isinstance(getattr(self, i), (tuple, Theta)):
                    self.ptype[getattr(TransportType, i.upper())
                               ] = ParameterType.UNCERTAIN
                    mpvar_ = create_mpvar(value=getattr(
                        self, i), component=self, ptype=getattr(MPVarType, i.upper()))
                    setattr(self, i, mpvar_)

        # * ---------- Collect factors -------------------------------
        # This will be done at Network level

        self.ftype, self.factors = dict(), dict()

        # *-----------------Set etype (Emission)---------------------------------
        # Types of emission accounted for are declared here and EmissionTypes are set

        self.etype = []
        self.emissions = dict()
        for i in ['gwp', 'odp', 'acid', 'eutt', 'eutf', 'eutm']:
            if getattr(self, i) is not None:
                self.etype.append(getattr(EmissionType, i.upper()))
                self.emissions[i] = getattr(self, i)

        # *----------------- Depreciation Warnings------------------------------------
        if self.trans_max is not None:
            raise ValueError(
                f'{self.name}: trans_max has been depreciated. Please use cap_max instead')

        if self.trans_min is not None:
            raise ValueError(
                f'{self.name}: trans_max has been depreciated. Please use cap_min instead')

        if self.varying is not None:
            raise ValueError(
                f'{self.name}: varying has been depreciated. Variability will be determined from factors provided to Network')

        if self.emission is not None:
            raise ValueError(
                f'{self.name}: emission has been depreciated. Please provide individual emissions (gwp, odp, acid, eutt, eutf, eutm) instead')

        # *----------------- Generate Random Name---------------------------------
        # A random name is generated if self.name = None

        if self.name is None:
            self.name = f'{self.__class__.__name__}_{uuid.uuid4().hex}'

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
