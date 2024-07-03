"""energiapy.Process - converts one Resource to another Resource, Or stores Resource  
"""
# TODO - diff between storage_loss and conversion efficiency

import operator
import uuid
from dataclasses import dataclass
from functools import reduce
from typing import Dict, List, Set, Tuple, Union

from ..utils.data_utils import get_depth
from .type.process import ProcessType
from .material import Material
from ..parameters.factor import Factor
from ..parameters.mpvar import Theta, create_mpvar
from ..parameters.type import *
from .parameters.process import ProcessParamType
from .parameters.special import BigM, CouldBeVar
from .resource import Resource


@dataclass
class Process:
    """
    A Process can produce or store Resource(s) 

    For production process:
        conversion needs to be specified
        production modes and material modes can be declared using nested dictionaries. See examples []
        piece wise linear capex curves can be declared using a dictionary. See examples []

    For storage process:
    storage = energiapy.Resource is needed. See examples []
    a resource_storage with the name {process name}_{resource name}_stored is created, which features in the resource balance 
    This new resource will inherit the store_max and store_min from Process even if it was specified for Resource
    cap_max and cap_min in this case will bound the maximum rate of charging and discharging 
    Further, when provided to a Location, a discharge Process is also created
    The expenditures (capex, fopex, vopex, incidental) are set to 0 if provided, None otherwise

    Given that maximum and minimum capacity (cap_max and cap_min), and expenditure (capex, fopex, vopex, incidental) can vary by location,
    localization can be achieved by providing the cap_max_localize, cap_min_localize, capex_localize, fopex_localize, vopex_localize, incidental_localize
    at Location level

    Credits need to be provided at Location

    Args:
        name (str): name of process. Enter None to randomly assign a name.
        cap_max (Union[float, Tuple[float], Theta, bool, 'Big']): Maximum production capacity allowed in a time period of the scheduling scale.
        cap_min (Union[float, dict, Tuple[float], Theta], optional): Minimum production capacity allowed in a time period of the scheduling scale. Defaults to None.
        land (Union[float, Tuple[float], Theta], optional): land requirement per unit basis. Defaults to None.
        conversion (Union[Dict[Union[int, str],Dict[Resource, float]], Dict[Resource, float]], optional): conversion data (Dict[Resource, float]]), if multimode the of form Dict[int,Dict[Resource, float]]. Defaults to None.
        material_cons (Union[Dict[Union[int, str], Dict[Material, float]],Dict[Material, float]], optional): Materials consumed per unit basis of production capacity. Defaults to None.
        capex (Union[float, dict, Tuple[float], Theta], None): Capital expenditure per unit basis, can be scaled with capacity. Defaults to None.
        fopex (Union[float, Tuple[float], Theta], None): Fixed operational expenditure per unit basis, can be scaled with capacity. Defaults to None.
        vopex (Union[float, Tuple[float], Theta], None): Variable operational expenditure per unit basis, can be scaled with capacity. Defaults to None.
        incidental (Union[float, Tuple[float], Theta], None): Incidental expenditure. Defaults to None.
        gwp (Union[float, Tuple[float], Theta], optional): global warming potential for settting up facility per unit basis. Defaults to None.
        odp (Union[float, Tuple[float], Theta], optional): ozone depletion potential for settting up facility per unit basis. Defaults to None.
        acid (Union[float, Tuple[float], Theta], optional): acidification potential for settting up facility per unit basis. Defaults to None.
        eutt (Union[float, Tuple[float], Theta], optional): terrestrial eutrophication potential for settting up facility per unit basis. Defaults to None.
        eutf (Union[float, Tuple[float], Theta], optional): fresh water eutrophication potential for settting up facility per unit basis. Defaults to None.
        eutm (Union[float, Tuple[float], Theta], optional): marine eutrophication potential for settting up facility per unit basis. Defaults to None.
        introduce (int, optional): Time period in the network scale when introduced. Defaults to None.
        lifetime (Union[float, Tuple[float], Theta] = None, optional): the expected lifetime of Process. Defaults to None.
        retire (int, optional): Time period in the network scale when retired. Defaults to None.
        p_fail (Union[float, Tuple[float], Theta] = None, optional): failure rate of Process. Defaults to None.
        storage(Resource, optional): Resource that can be stored in process. Defaults to None.
        store_max (Union[float, Tuple[float], Theta] = None, optional): Maximum allowed storage of resource in process. Defaults to None.
        store_min (Union[float, Tuple[float], Theta] = None, optional): Minimum allowed storage of resource in process. Defaults to None.
        storage_cost: (Union[float, Tuple[float], Theta] = None, optional): penalty for mainting inventory per time period in the scheduling scale. Defaults to None.
        store_loss: (Union[float, Tuple[float], Theta] = None, optional): resource loss on the scheduling scale. Defaults to None. 
        basis(str, optional): base units for operation. Defaults to 'unit'.
        block (str, optional): define block for convenience. Defaults to None.
        label(str, optional):Longer descriptive label if required. Defaults to None.
        citation (str, optional): citation for data. Defaults to 'citation needed'.
        trl (str, optional): technology readiness level. Defaults to None.
        ctype (List[Union[ProcessType, Dict[ProcessType, Set['Location']]]], optional): list of process ctypes. Defaults to None
        ptype (Dict[ProcessParamType, Union[ParameterType, Dict['Location', ParameterType]]], optional): paramater type of declared values . Defaults to None
        ltype (Dict[ProcessParamType, List[Tuple['Location', LocalizationType]]], optional): which parameters are localized. Defaults to None.
        ftype (Dict[ProcessParamType, List[Tuple['Location',FactorType]]], optional): which parameters are provided with factors at Location. Defaults to None
        etype (List[EmissionType], optional): list of emission types defined. Defaults to None
        localizations (Dict[ProcessParamType, List[Tuple['Location', Localization]]], optional): collects localizations when defined at Location. Defaults to None.
        factors (Dict[ProcessParamType, List[Tuple['Location', Factor]]], optional): collects factors when defined at Location. Defaults to None.
        emissions (Dict[str, float], optional): collects emission data. Defaults to None.

    Examples:
        For processes with varying production capacity

        >>> WF = Process(name='WF', conversion={Wind: -1, Power: 1}, capex= 100, Fopex= 10, Vopex= 1,cap_max=100, gwp=52700, land= 90, basis = 'MW', block='power', label='Wind mill array')

        For process with multiple modes of operation

        >>> PEM = Process(name = 'PEM', conversion = {1: {Power: -1, H2: 19.474, O2: 763.2, H2O: -175.266}, 2: {Power: -1, H2: 1.2*19.474, O2: 1.2*763.2, H2O: 1.2*-175.266}, cap_max= 100, capex = 784000, label = 'PEM Electrolysis')

        For process with multiple resource inputs

        >>> CoolCar = Process(name = 'CoolCar', conversion = {1: {Power: -1, Mile: 1}, 2: {H2: -1, Mile:2}, cap_max= 50, capex = 70, label = 'CoolCar')

    """

    name: str
    # Design parameters
    cap_max: Union[float, Tuple[float], Theta, bool, 'Big']
    cap_min: float = None
    land: float = None  # Union[float, Tuple[float], Theta]
    conversion: Union[Dict[Union[int, str], Dict[Resource, float]],
                      Dict[Resource, float]] = None
    material_cons: Union[Dict[Union[int, str],
                              Dict[Material, float]], Dict[Material, float]] = None
    # Expenditure
    capex: Union[float, dict, Tuple[float], Theta] = None
    fopex: Union[float, Tuple[float], Theta] = None
    vopex: Union[float, Tuple[float], Theta] = None
    incidental: Union[float, Tuple[float], Theta] = None
    # Emission
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
    # These go to storage_resource defined in STORAGE Process
    storage: Resource = None
    store_max: Union[float, Tuple[float], Theta, bool, 'Big'] = None
    store_min: float = None
    storage_cost: Union[float, Tuple[float], Theta] = None
    store_loss: Union[float, Tuple[float], Theta] = None
    # Types
    ctype: List[Union[ProcessType, Dict[ProcessType, Set['Location']]]] = None
    ptype: Dict[ProcessParamType, Union[ParameterType,
                                        Dict['Location', ParameterType]]] = None
    ltype: Dict[ProcessParamType,
                List[Tuple['Location', LocalizationType]]] = None
    ftype: Dict[ProcessParamType, List[Tuple['Location', FactorType]]] = None
    etype: List[EmissionType] = None
    # Collections
    localizations: Dict[ProcessParamType,
                        List[Tuple['Location', Localization]]] = None
    factors: Dict[ProcessParamType, List[Tuple['Location', Factor]]] = None
    emissions: Dict[str, float] = None
    # Details
    basis: str = None
    block: str = None
    citation: str = None
    label: str = None
    trl: str = None
    # Depreciated
    varying: list = None
    prod_max: float = None
    prod_min: float = None

    def __post_init__(self):

        # *-----------------Set ctype (ProcessType)---------------------------------

        if not self.ctype:
            self.ctype = list()

        # conversion can be single mode (SINGLE_PRODMODE) or multimode (MULTI_PRODMODE)
        # For MULTI_PRODMODE, a dict of type {'mode' (str, int) : {Resource: float}} needs to be provided

        if self.conversion:
            if get_depth(self.conversion) > 1:
                self.ctype.append(ProcessType.MULTI_PRODMODE)
                self.prod_modes = set(self.conversion)
                self.resources = reduce(
                    operator.or_, (set(self.conversion[i]) for i in self.prod_modes), set())
            else:
                self.ctype.append(ProcessType.SINGLE_PRODMODE)
                self.resources = set(self.conversion)

        # Materials are not necessarily consumed (NO_MATMODE), if material_cons is None
        # If consumed, there could be multiple modes of consumption (MULTI_MATMODE) or one (SINGLE_MATMODE)
        # for MULTI_MATMODE, provide a dict of type ('material_mode' (str, int): {Material: float})

        if self.material_cons is None:
            self.ctype.append(ProcessType.NO_MATMODE)
            self.materials = set()

        else:
            if get_depth(self.material_cons) > 1:
                self.ctype.append(ProcessType.MULTI_MATMODE)
                self.material_modes = set(self.material_cons)
                self.materials = reduce(
                    operator.or_, (set(self.material_cons[i]) for i in self.material_modes), set())
            else:
                self.ctype.append(ProcessType.SINGLE_MATMODE)
                self.materials = set(self.material_cons)

        # If a Resource is provide for self.storage, a storage resource is created
        # This resource has the name Process_Resource_stored
        # conversion_discharge is created while accounting for storage_loss
        # Do not provide a conversion if declaring a .STORAGE type Process

        if self.storage:
            self.ctype.append(ProcessType.STORAGE)
            if self.store_loss is None:
                self.store_loss = 0
            # create a dummy resource if process is storage type.
            self.resource_storage = self.create_storage_resource(
                resource=self.storage)
            # efficiency of input to storage is 100 percent
            self.conversion = {self.storage: -1, self.resource_storage: 1}
            self.conversion_discharge = {
                self.resource_storage: -1, self.storage: 1*(1 - self.store_loss)}  # the losses are all at the output (retrival)
            self.resources = set(self.conversion)

        # capex can be linear (LINEAR_CAPEX) or piecewise linear (PWL_CAPEX)
        # if PWL, capex needs to be provide as a dict {capacity_segment: capex_segement}
        if self.capex:
            if isinstance(self.capex, dict):
                self.ctype.append(ProcessType.PWL_CAPEX)
                self.capacity_segments = list(self.capex)
                self.capex_segments = list(self.capex.values())
            else:
                self.ctype.append(ProcessType.LINEAR_CAPEX)

        # if any expenditure is incurred
        if any([self.capex, self.fopex, self.vopex, self.incidental]):
            self.ctype.append(ProcessType.EXPENDITURE)

        # if it requires land to set up
        if self.land:
            self.ctype.append(ProcessType.LAND)

        # if this process fails
        if self.p_fail:
            self.ctype.append(ProcessType.FAILURE)

        # if this process has some readiness aspects defined
        if any([self.introduce, self.retire, self.lifetime]):
            self.ctype.append(ProcessType.READINESS)

        # *-----------------Set ptype (Parameter)---------------------------------
        # ptypes of declared parameters are set to .UNCERTAIN if a MPVar Theta or a tuple of bounds is provided,
        # .CERTAIN otherwise
        # If empty Theta is provided, the bounds default to (0, 1)
        # Factors can be declared at Location (Location, DataFrame), gets converted to  (Location, Factor)

        for i in self.process_level_parameters():
            self.update_process_parameter(parameter=i)

        # *-----------------Set etype (Emission)---------------------------------
        # Types of emission accounted for are declared here and EmissionTypes are set

        for i in self.etypes():
            attr_ = getattr(self, i.lower())
            etype_ = getattr(EmissionType, i)
            if attr_:
                if not self.etype:  # if etype is not yet defined
                    self.etype = []
                    self.emissions = dict()
                    self.ctype.append(ProcessType.EMISSION)
                self.etype.append(etype_)
                self.emissions[i.lower()] = attr_

        # *----------------- Generate Random Name---------------------------------
        # A random name is generated if self.name = None

        if not self.name:
            self.name = f'{self.class_name()}_{uuid.uuid4().hex}'

        # *----------------- Depreciation Warnings------------------------------------

        if self.prod_max:
            raise ValueError(
                f'{self.name}: prod_max has been depreciated. Please use cap_max instead')
        if self.prod_min:
            raise ValueError(
                f'{self.name}: prod_min has been depreciated. Please use cap_min instead')
        if self.varying:
            raise ValueError(
                f'{self.name}: varying has been depreciated. Variability will be intepreted based on data provided to energiapy.Location factors')

    # *----------------- Properties ---------------------------------

    @property
    def capacity(self):
        """Sets capacity
        """
        if self.cap_max:
            return CouldBeVar

    # *----------------- Class Methods ---------------------------------

    @classmethod
    def class_name(cls) -> str:
        """Returns class name 
        """
        return cls.__name__

    # * parameter types

    @classmethod
    def ptypes(cls) -> Set[str]:
        """All Process paramters
        """
        return ProcessParamType.all()

    @classmethod
    def process_level_parameters(cls) -> Set[str]:
        """Set when Process is declared
        """
        return ProcessParamType.process_level()

    @classmethod
    def process_level_resource_parameters(cls) -> Set[str]:
        """Resource parameters set when Process is declared
        """
        return ProcessParamType.process_level_resource()

    @classmethod
    def location_level_parameters(cls) -> Set[str]:
        """Set when Location is declared
        """
        return ProcessParamType.location_level()

    @classmethod
    def process_level_readiness_parameters(cls) -> Set[str]:
        """Set when Process are declared
        """
        return ProcessParamType.readiness()

    @classmethod
    def process_level_failure_parameters(cls) -> Set[str]:
        """Set when Process are declared
        """
        return ProcessParamType.failure()

    @classmethod
    def uncertain_parameters(cls) -> Set[str]:
        """Uncertain parameters
        """
        return ProcessParamType.uncertain()

    @classmethod
    def uncertain_factors(cls) -> Set[str]:
        """Uncertain parameters for which factors are defined
        """
        return ProcessParamType.uncertain_factor()

    @classmethod
    def process_level_uncertain_parameters(cls) -> Set[str]:
        """Uncertain parameters set a Process level
        """
        return ProcessParamType.process_level_uncertain()

    @classmethod
    def location_level_uncertain_parameters(cls) -> Set[str]:
        """Uncertain parameters set a Location level
        """
        return ProcessParamType.location_level_uncertain()

    # * component class types

    @classmethod
    def ctypes(cls) -> Set[str]:
        """All Process paramters
        """
        return ProcessType.all()

    @classmethod
    def process_level_classifications(cls) -> Set[str]:
        """Set when Process is declared
        """
        return ProcessType.process_level()

    @classmethod
    def location_level_classifications(cls) -> Set[str]:
        """Set when Location is declared
        """
        return ProcessType.location_level()

    # * localization types

    @classmethod
    def ltypes(cls) -> Set[str]:
        """Process parameters than can be localized 
        """
        return ProcessParamType.localize()

    # * factor types

    @classmethod
    def ftypes(cls) -> Set[str]:
        """Factor types
        """
        return ProcessParamType.uncertain_factor()

    # * emission types

    @classmethod
    def etypes(cls) -> Set[str]:
        """Emission types
        """
        return EmissionType.all()

    # *----------------- Functions ---------------------------------------------

    def update_process_parameter(self, parameter: str):
        """updates parameter, sets ptype

        Args:
            parameter (str): parameter to update 
        """
        attr_ = getattr(self, parameter.lower())
        if attr_:
            ptype_ = getattr(ProcessParamType, parameter)
            if not self.ptype:
                self.ptype = dict()
            if isinstance(attr_, (tuple, Theta)):
                self.ptype[ptype_] = ParameterType.UNCERTAIN
                mpvar_ = create_mpvar(
                    value=attr_, component=self, ptype=getattr(MPVarType, f'{self.class_name()}_{parameter}'.upper()))
                setattr(self, parameter.lower(), mpvar_)
            elif hasattr(attr_, 'bigm') or attr_ is True:
                self.ptype[ptype_] = ParameterType.BIGM
                if attr_ is True:
                    setattr(self, parameter.lower(), BigM)
            elif hasattr(attr_, 'couldbevar'):
                self.ptype[ptype_] = ParameterType.UNDECIDED
            else:
                self.ptype[ptype_] = ParameterType.CERTAIN

    def create_storage_resource(self, resource: Resource) -> Resource:
        """Creates a resource for storage, used if ProcessType is STORAGE

        Args:
            resource (Resource): Resource to be stored
        Returns:
            Resource: of ResourceType.STORE, named Process.name_Resource.name_stored
        """

        return Resource(name=f"{self.name}_{resource.name}_stored", store_loss=self.store_loss, store_max=self.store_max, store_min=self.store_min,
                        storage_cost=self.storage_cost, label=f'{resource.label} stored in {self.label}')

    # *----------- Hashing --------------------------------

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
