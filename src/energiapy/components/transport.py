"""energiapy.Transport - moves Resources between Locations
"""
# TODO ---- apply material constraints
# TODO --- trans_loss, retire, introduce, land, land_cost (could be between location.. will need to check)
# TODO -- PWL CAPEX

import operator
import uuid
from dataclasses import dataclass
from functools import reduce
from typing import Dict, List, Set, Tuple, Union

from ..utils.data_utils import get_depth
from .location import Location
from .material import Material
from .model.factor import Factor
from .model.paramtype import FactorType, MPVarType, ParameterType
from .model.special import BigM, CouldBeVar
from .model.theta import Theta, birth_theta
from .model.transport import TransportParamType
from .resource import Resource
from .type.emission import EmissionType
from .type.resource import ResourceType
from .type.transport import TransportType


@dataclass
class Transport:
    """
    Transports move Resource from one Location to Another 

    Args:
        name(str): name of transport, short ones are better to deal with .
        resources(Set[Resource]): specific resources transported through mode.
        cap_max(Union[float, Tuple[float], Theta, bool, 'Big']): maximum capacity that can be set up.
        cap_min(Union[float, Tuple[float], Theta], optional): minimum capacity required to set up. Defaults to None.
        land(Union[float, Tuple[float], Theta], optional): land required to set up transport. Defaults to None.
        trans_loss(Union[float, Tuple[float], Theta], optional): transport losses per unit basis of Resource for timeperiod in scheduling scale. Defaults to 0.
        material_cons(Dict[Material, float], optional): Materials consumed per unit distance of Transport. Defaults to None.
        capex(Union[float, Tuple[float], Theta], optional): capital expenditure on a per unit distance unit capacity basis. Defaults to None.
        vopex(Union[float, Tuple[float], Theta], optional): variable operational expenditure on a per unit distance unit capacity basis. Defaults to None.
        fopex(Union[float, Tuple[float], Theta], optional): fixed operational expenditure on a per unit distance unit capacity basis. Defaults to None.
        incidental(float, optional): incidental expenditure on a per unit distance unit capacity basis. Defaults to None.
        gwp (Union[float, Tuple[float], Theta], optional): global warming potential for settting up transportation per unit distance. Defaults to None.
        odp (Union[float, Tuple[float], Theta], optional): ozone depletion potential for settting up transportation per unit distance. Defaults to None.
        acid (Union[float, Tuple[float], Theta], optional): acidification potential for settting up transportation per unit distance. Defaults to None.
        eutt (Union[float, Tuple[float], Theta], optional): terrestrial eutrophication potential for settting up transportation per unit distance. Defaults to None.
        eutf (Union[float, Tuple[float], Theta], optional): fresh water eutrophication potential for settting up transportation per unit distance. Defaults to None.
        eutm (Union[float, Tuple[float], Theta], optional): marine eutrophication potential for settting up transportation per unit distance. Defaults to None.
        introduce (int, optional): Time period in the network scale when introduced. Defaults to None.
        lifetime (Union[float, Tuple[float], Theta] = None, optional): the expected lifetime of Transport. Defaults to None.
        retire (int, optional): Time period in the network scale when retired. Defaults to None.
        p_fail (Union[float, Tuple[float], Theta] = None, optional): failure rate of Transport. Defaults to None.
        basis (str, optional): unit for measuring cost and distance. Defaults to None .
        block (Union[str, list, dict], optional): block to which it belong. Convinient to set up integer cuts. Defaults to None.
        label (str, optional): used while generating plots. Defaults to None.
        citation (str, optional): can provide citations for your data sources. Defaults to None.
        ctype (List[Union[TransportType, Dict[TransportType, Set[Tuple[Location, Location]]]]], optional): list of Transport ctypes. Defaults to None.
        aspect (Dict[LandType, ParameterType], optional): paramater type of declared values. Defaults to None.
        ftype (Dict[TransportType, Tuple[Tuple[Location, Location], FactorType]], optional): factor type of declared factors. Defaults to None. 
        etype (List[EmissionType], optional): list of emission types defined. Defaults to None
        factors (Dict[TransportParamType, Tuple[Tuple[Location, Location], Factor]], optional): collects factors when defined at Network. Defaults to None.
        emissions (Dict[str, float], optional): collects emission data. Defaults to None.

    Examples:

        Transport objects can be anything from Trains to Pipelines

        >>> Train = Transport(name='Train', resources={H2}, materials_cons={Steel: 100}, trans_max=10000, trans_loss=0.001, capex=300, label= 'Railine for Hydrogen)

    """

    name: str
    # Primary attributes
    resources: Set[Resource]
    cap_max: Union[float, Tuple[float], Theta, bool, 'Big']
    # Design Parameters
    cap_min: Union[float, Tuple[float], Theta] = None
    land: Union[float, Tuple[float], Theta] = None
    trans_loss: Union[float, Tuple[float], Theta] = None
    material_cons: Dict[Material, float] = None
    # Expenditure
    capex: Union[float, dict, Tuple[float], Theta] = None
    vopex: Union[float, Tuple[float], Theta] = None
    fopex: Union[float, Tuple[float], Theta] = None
    incidental: Union[float, dict, Tuple[float], Theta] = None
    # Emissions
    gwp: Union[float, Tuple[float], Theta] = None
    odp: Union[float, Tuple[float], Theta] = None
    acid: Union[float, Tuple[float], Theta] = None
    eutt: Union[float, Tuple[float], Theta] = None
    eutf: Union[float, Tuple[float], Theta] = None
    eutm: Union[float, Tuple[float], Theta] = None
    # Readiness
    introduce: Union[float, Tuple[float], Theta] = None
    retire: Union[float, Tuple[float], Theta] = None
    lifetime: Union[float, Tuple[float], Theta] = None
    p_fail: Union[float, Tuple[float], Theta] = None
    # Details
    basis: str = None
    block: str = None
    label: str = None
    citation: str = None
    # Type
    ctype: List[Union[TransportType,
                      Dict[TransportType, Set[Tuple[Location, Location]]]]] = None
    aspect: Dict[TransportParamType, ParameterType] = None
    ftype: Dict[TransportParamType,
                Tuple[Tuple[Location, Location], FactorType]] = None
    etype: List[EmissionType] = None
    # Collections
    factors: Dict[TransportParamType,
                  Tuple[Tuple[Location, Location], Factor]] = None
    emissions: Dict[str, float] = None

    # Depricated
    trans_max: float = None
    trans_min: float = None
    emission: float = None
    varying: bool = None

    def __post_init__(self):

        # *-----------------Set ctype (TransportType)---------------------------------

        if not self.ctype:
            self.ctype = list()

        for i in self.resources:  # update Resource if transported
            # TODO - FIX

            i.ctype.append(ResourceType.TRANSPORT)
            if ResourceType.IMPLICIT in i.ctype:
                i.ctype.remove(ResourceType.IMPLICIT)
            if not i.transport:
                i.transport = set()
            i.transport.add(self)

        # Materials are not necessarily consumed (NO_MATMODE), if material_cons is None
        # If consumed, there could be multiple modes of consumption (MULTI_MATMODE) or one (SINGLE_MATMODE)
        # for MULTI_MATMODE, provide a dict of type ('material_mode' (str, int): {Material: float})

        if self.material_cons is None:
            self.ctype.append(TransportType.NO_MATMODE)
            self.materials = set()

        else:
            if get_depth(self.material_cons) > 1:
                self.ctype.append(TransportType.MULTI_MATMODE)
                self.material_modes = set(self.material_cons)
                self.materials = reduce(
                    operator.or_, (set(self.material_cons[i]) for i in self.material_modes), set())

            else:
                self.ctype.append(TransportType.SINGLE_MATMODE)
                self.materials = set(self.material_cons)

        # capex can be linear (LINEAR_CAPEX) or piecewise linear (PWL_CAPEX)
        # if PWL, capex needs to be provide as a dict {capacity_segment: capex_segement}
        if self.capex:
            if isinstance(self.capex, dict):
                self.ctype.append(TransportType.PWL_CAPEX)
                self.capacity_segments = list(self.capex)
                self.capex_segments = list(self.capex.values())
            else:
                self.ctype.append(TransportType.LINEAR_CAPEX)

        # if any expenditure is incurred
        if any([self.capex, self.fopex, self.vopex, self.incidental]):
            self.ctype.append(TransportType.EXPENDITURE)

        # if it requires land to set up
        if self.land:
            self.ctype.append(TransportType.LAND)

        # if this process fails
        if self.p_fail:
            self.ctype.append(TransportType.FAILURE)

        # if this process has some readiness aspects defined
        if any([self.introduce, self.retire, self.lifetime]):
            self.ctype.append(TransportType.READINESS)

        # *-----------------Set aspect---------------------------------
        # If parameter provided as Theta or tuple bounds are provided - makes MPVar

        self.aspect = dict()

        for i in self.aspects():
            self.update_transport_level_parameter(parameter=i)

        # *-----------------Set etype (Emission)---------------------------------
        # Types of emission accounted for are declared here and EmissionTypes are set

        for i in self.etypes():
            attr_ = getattr(self, i.lower())
            etype_ = getattr(EmissionType, i)
            if attr_:
                if not self.etype:  # if etype is not yet defined
                    self.etype = []
                    self.emissions = dict()
                    self.ctype.append(TransportType.EMISSION)
                self.etype.append(etype_)
                self.emissions[i.lower()] = attr_


        # *----------------- Depreciation Warnings------------------------------------
        if self.trans_max:
            raise ValueError(
                f'{self.name}: trans_max has been depreciated. Please use cap_max instead')

        if self.trans_min:
            raise ValueError(
                f'{self.name}: trans_max has been depreciated. Please use cap_min instead')

        if self.varying:
            raise ValueError(
                f'{self.name}: varying has been depreciated. Variability will be determined from factors provided to Network')

        if self.emission:
            raise ValueError(
                f'{self.name}: emission has been depreciated. Please provide individual emissions (gwp, odp, acid, eutt, eutf, eutm) instead')

    # *----------------- Properties ---------------------------------

    @property
    def capacity(self):
        """Sets capacity
        """
        if self.cap_max:
            return CouldBeVar

    # *----------------- Class Methods -------------------------------------

    @classmethod
    def class_name(cls) -> str:
        """Returns class name 
        """
        return cls.__name__

    # * Transport parameters

    @classmethod
    def aspects(cls) -> Set[str]:
        """All Transport paramters
        """
        return TransportParamType.all()

    @classmethod
    def uncertain_parameters(cls) -> Set[str]:
        """Uncertain parameters
        """
        return TransportParamType.uncertain()

    @classmethod
    def uncertain_factors(cls) -> Set[str]:
        """Uncertain parameters for which factors are defined
        """
        return TransportParamType.uncertain_factor()

    @classmethod
    def transport_level_readiness_parameters(cls) -> Set[str]:
        """Set when Transport are declared
        """
        return TransportParamType.readiness()

    @classmethod
    def transport_level_failure_parameters(cls) -> Set[str]:
        """Set when Transport are declared
        """
        return TransportParamType.failure()

    # * Transport classifications

    @classmethod
    def ctypes(cls) -> Set[str]:
        """All Transport paramters
        """
        return TransportType.all()

    @classmethod
    def transport_level_classifications(cls) -> Set[str]:
        """Set when Transport is declared
        """
        return TransportType.transport_level()

    @classmethod
    def network_level_classifications(cls) -> Set[str]:
        """Set when Network is declared
        """
        return TransportType.network_level()

    # * factor types

    @classmethod
    def ftypes(cls) -> Set[str]:
        """Factor types
        """
        return TransportParamType.uncertain_factor()

    # * emission types

    @classmethod
    def etypes(cls) -> Set[str]:
        """Emission types
        """
        return EmissionType.all()

    # *----------------- Functions ---------------------------------------------

    def update_transport_level_parameter(self, parameter: str):
        """updates parameter, sets aspect

        Args:
            parameter (str): parameter to update 
        """
        attr_ = getattr(self, parameter.lower())
        if attr_:
            aspect_ = getattr(TransportParamType, parameter)
            if isinstance(attr_, (tuple, Theta)):
                self.aspect[aspect_] = ParameterType.UNCERTAIN
                theta_ = birth_theta(
                    value=attr_, component=self, aspect=getattr(MPVarType, f'{self.cname}_{parameter}'.upper()))
                setattr(self, parameter.lower(), theta_)
            elif hasattr(attr_, 'bigm') or attr_ is True:
                self.aspect[aspect_] = ParameterType.BIGM
                if attr_ is True:
                    setattr(self, parameter.lower(), BigM)
            elif hasattr(attr_, 'couldbevar'):
                self.aspect[aspect_] = ParameterType.UNDECIDED
            else:
                self.aspect[aspect_] = ParameterType.CERTAIN

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
