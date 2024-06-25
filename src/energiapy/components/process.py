"""energiapy.Process - converts one Resource to another Resource, Or stores Resource  
"""
# TODO - diff between storage_loss and conversion efficiency

import uuid
from dataclasses import dataclass
from typing import Dict, List, Tuple, Union

from ..utils.data_utils import get_depth
from .comptype.emission import EmissionType
from .comptype.process import ProcessType
from .material import Material
from .parameters.mpvar import Theta, create_mpvar
from .parameters.paramtype import (FactorType, LocalizeType, MPVarType,
                                   ParameterType)
from .parameters.process import ProcessParamType
from .comptype.process import ProcessType
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
        cap_max (Union[float, dict, Tuple[float], Theta]): Maximum production capacity allowed in a time period of the scheduling scale.
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
        lifetime (Union[float, Tuple[float], Theta] = None, optional): the expected lifetime of process. Defaults to None.
        retire (int, optional): Time period in the network scale when retired. Defaults to None.
        p_fail (Union[float, Tuple[float], Theta] = None, optional): failure rate of process. Defaults to None.
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
        ctype (List[ProcessType], optional): process type. Defaults to None
        ptype (Dict[ProcessType, List[Tuple['Location', ParameterType]]], optional): paramater type of declared values . Defaults to None
        ltype (Dict[ProcessType, List[Tuple['Location', LocalizeType]]], optional): which parameters are localized. Defaults to None.
        ftype (Dict[ProcessType, List[Tuple['Location',FactorType]]], optional): which parameters are provided with factors at Location. Defaults to None


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
    cap_max: Union[float, dict, Tuple[float], Theta]
    cap_min: Union[float, dict, Tuple[float], Theta] = None
    land: Union[float, Tuple[float], Theta] = None
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
    # Temporal
    introduce: Union[float, Tuple[float], Theta] = None
    retire: Union[float, Tuple[float], Theta] = None
    lifetime: Union[float, Tuple[float], Theta] = None
    p_fail: Union[float, Tuple[float], Theta] = None
    # These go to storage_resource defined in STORAGE Process
    storage: Resource = None
    store_max: Union[float, Tuple[float], Theta] = None
    store_min: Union[float, Tuple[float], Theta] = None
    storage_cost: Union[float, Tuple[float], Theta] = None
    store_loss: Union[float, Tuple[float], Theta] = None
    # Types
    ctype: List[ProcessType] = None
    ptype: Dict[ProcessType, ParameterType] = None
    ltype: Dict[ProcessType, List[Tuple['Location', LocalizeType]]] = None
    ftype: Dict[ProcessType, List[Tuple['Location', FactorType]]] = None
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

    # Update ProcessType, FactorType, LocalizeType, EmissionType as necessary if adding attributes

    def __post_init__(self):

        # *-----------------Declared at location---------------------------------

        # Dict['Location', Union[float, Tuple[float], Theta]]. Declared at Location
        self.credit = None  # credits inclured by Process
        self.capacity = None  # maximum !established! capacity that can be utilized

        # *-----------------Set ctype (ProcessType)---------------------------------

        if self.ctype is None:
            self.ctype = []

        # for i in self.parameters_declared_here():
        #     if getattr(self, i) is not None:
        #         self.ctype.append(getattr(ProcessType, i.upper()))

        # if self.cap_max is not None:
        #     # This is for variability of capacity that can be utilized (scheduling level)and not capacity expansion (design level)
        #     self.ctype.append(ProcessType.CAPACITY)

        # CAPEX can be linear (LINEAR_CAPEX) or piecewise linear (PWL_CAPEX)
        # if PWL, capex needs to be provide as a dict {capacity_segment: capex_segement}
        if self.capex is not None:
            if isinstance(self.capex, dict):
                self.ctype.append(ProcessType.PWL_CAPEX)
                self.capacity_segments = list(self.capex.keys())
                self.capex_segments = list(self.capex.values())
            else:
                self.ctype.append(ProcessType.LINEAR_CAPEX)

        # conversion can be single mode (SINGLE_PRODMODE) or multimode (MULTI_PRODMODE)
        # For MULTI_PRODMODE, a dict of type {'mode' (str, int) : {Resource: float}} needs to be provided

        if self.conversion is not None:
            if get_depth(self.conversion) > 1:
                self.ctype.append(ProcessType.MULTI_PRODMODE)
                self.prod_modes = set(self.conversion.keys())
                self.resource_req = set().union(
                    *[set(self.conversion[i].keys()) for i in self.prod_modes])
            else:
                self.ctype.append(ProcessType.SINGLE_PRODMODE)
                self.resource_req = set(self.conversion.keys())

        # Materials are not necessarily consumed (NO_MATMODE), if material_cons is None
        # If consumed, there could be multiple modes of consumption (MULTI_MATMODE) or one (SINGLE_MATMODE)
        # for MULTI_MATMODE, provide a dict of type ('material_mode' (str, int): {Material: float})

        if self.material_cons is None:
            self.ctype.append(ProcessType.NO_MATMODE)

        else:
            if get_depth(self.material_cons) > 1:
                self.ctype.append(ProcessType.MULTI_MATMODE)
                self.material_modes = set(self.material_cons.keys())
                self.material_req = set().union(
                    *[set(self.material_cons[i].keys()) for i in self.material_modes])
            else:
                self.ctype.append(ProcessType.SINGLE_MATMODE)
                self.material_req = set(self.material_cons.keys())

        # If a Resource is provide for self.storage, a storage resource is created
        # This resource has the name Process_Resource_stored
        # conversion_discharge is created while accounting for storage_loss
        # Do not provide a conversion if declaring a .STORAGE type Process

        if self.storage is not None:
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
            self.resource_req = set(self.conversion.keys())

        # *-----------------Set ptype (Parameter)---------------------------------
        # Default all declared parameters to .CERTAIN initially
        # They are replaced by .UNCERTAIN if a MPVar Theta or a tuple of bounds is provided
        # If empty Theta is provided, the bounds default to (0, 1)
        # They are replaced by a list of (Location, .FactorType) if factors are declared at Location

        # self.ptype = {i: ParameterType.CERTAIN for i in self.ctype}

        self.ptype = dict()

        # for i in self.parameters_declared_here():
        #     if getattr(self, i) is not None:
        #         ctype_ = getattr(ProcessType, i.upper())
        #         if i in self.mpvar_parameters():

        # for i in list(set(self.parameters_declared_here()) & set(self.mpvar_parameters())):
        #     if getattr(self, i) is not None:
        #         ctype_ = getattr(ProcessType, i.upper())
        #         if isinstance(getattr(self, i), (tuple, Theta)):
        #             self.ptype[ctype_] = ParameterType.UNCERTAIN
        #             mpvar_ = create_mpvar(value=getattr(self, i),
        #                                   component=self, ptype=getattr(MPVarType, i.upper()))
        #             setattr(self, i, mpvar_)
        #         else:
        #             self.ptype[ctype_] = ParameterType.CERTAIN

        # *-----------------Set etype (Emission)---------------------------------
        # Types of emission accounted for are declared here and EmissionTypes are set

        self.etype = []
        self.emissions = dict()
        for i in self.etypes():
            if getattr(self, i) is not None:
                self.etype.append(getattr(EmissionType, i.upper()))
                self.emissions[i] = getattr(self, i)

        # *----------------- Set ltype ---------------------------------
        # Localization factors can be provided for parameters at Location
        # These include 'cap_max', 'cap_min', 'capex', 'fopex', 'vopex', 'incidental' (if declared)
        # ltype is a Dict[ProcessType, List[Tuple['Location', LocalizeType]]]
        # localizations a Dict[ProcessType, List[Tuple['Location', Localize]]]

        self.ltype, self.localizations = dict(), dict()

        # *------------ Collect Factors and Localizations at Location -----------
        # Deterministic data sets can be provided as factors for parameters at location
        # These include 'cap_max', 'cap_min', 'capex', 'fopex', 'vopex', 'incidental'
        # ftype is a Dict[ProcessType, List[Tuple['Location', FactorType]]]
        # factors a Dict[ProcessType, List[Tuple['Location', Factor]]]

        self.ftype, self.factors = dict(), dict()

        # *----------------- Generate Random Name---------------------------------
        # A random name is generated if self.name = None

        if self.name is None:
            self.name = f'{self.__class__.__name__}_{uuid.uuid4().hex}'

        # *----------------- Depreciation Warnings------------------------------------

        if self.prod_max is not None:
            raise ValueError(
                f'{self.name}: prod_max has been depreciated. Please use cap_max instead')
        if self.prod_min is not None:
            raise ValueError(
                f'{self.name}: prod_min has been depreciated. Please use cap_min instead')
        if self.varying is not None:
            raise ValueError(
                f'{self.name}: varying has been depreciated. Variability will be intepreted based on data provided to energiapy.Location factors')

    # *----------------- Class Methods ---------------------------------------------

    @classmethod
    def parameters(cls) -> List[str]:
        """All Process paramters
        """
        return ProcessParamType.all()

    @classmethod
    def process_level_parameters(cls) -> List[str]:
        """Set when Process is declared
        """
        return ProcessParamType.process_level()

    @classmethod
    def process_level_resource_parameters(cls) -> List[str]:
        """Resource parameters set when Process is declared
        """
        return ProcessParamType.process_level_resource()

    @classmethod
    def location_level_parameters(cls) -> List[str]:
        """Set when Location is declared
        """
        return ProcessParamType.location_level()

    @classmethod
    def process_level_temporal_parameters(cls) -> List[str]:
        """Set when Process are declared
        """
        return ProcessParamType.temporal()

    @classmethod
    def uncertain_parameters(cls) -> List[str]:
        """Uncertain parameters
        """
        return ProcessParamType.uncertain()

    @classmethod
    def localize_parameters(cls) -> List[str]:
        """Process parameters than can be localized 
        """
        return ProcessParamType.localize()

    @classmethod
    def classifications(cls) -> List[str]:
        """All Process paramters
        """
        return ProcessType.all()

    @classmethod
    def process_level_classifications(cls) -> List[str]:
        """Set when Process is declared
        """
        return ProcessType.process_level()

    @classmethod
    def location_level_classifications(cls) -> List[str]:
        """Set when Location is declared
        """
        return ProcessType.location_level()

    # @classmethod
    # def ftypes(cls) -> List[str]:
    #     """Factor types
    #     """
    #     return [i.lower() for i in FactorType.process()]

    # @classmethod
    # def ltypes(cls) -> List[str]:
    #     """Localization types
    #     """
    #     return [i.lower() for i in LocalizeType.process()]

    @classmethod
    def etypes(cls) -> List[str]:
        """Emission types
        """
        return EmissionType.all()
    # *----------------- Functions ---------------------------------------------

    def create_storage_resource(self, resource: Resource) -> Resource:
        """Creates a resource for storage, used if ProcessType is STORAGE

        Args:
            resource (Resource): Resource to be stored
        Returns:
            Resource: of ResourceType.STORE, named Process.name_Resource.name_stored
        """

        return Resource(name=f"{self.name}_{resource.name}_stored", store_loss=self.store_loss, store_max=self.store_max, store_min=self.store_min,
                        storage_cost=self.storage_cost, label=f'{resource.label} stored in {self.label}')

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
