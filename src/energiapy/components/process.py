"""energiapy.Process - converts one Resource to another Resource, Or stores Resource  
"""

import uuid
from dataclasses import dataclass
from typing import Dict, List, Tuple, Union
from warnings import warn

from ..utils.data_utils import get_depth
from .comptype import EmissionType, ProcessType, ResourceType
from .material import Material
from .parameters.factor import Factor
from .parameters.mpvar import Theta, create_mpvar
from .parameters.paratype import (FactorType, LocalizeType, MPVarType,
                                  ParameterType)
from .resource import Resource


@dataclass
class Process:

    """
    Processes can be of produce or store resources 

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

    Args:
        name (str): name of process. Enter None to randomly assign a name.
        cap_max (Union[float, dict], optional): Maximum production capacity allowed in a time period of the scheduling scale. Defaults to None.
        cap_min (Union[float, dict], optional): Minimum production capacity allowed in a time period of the scheduling scale. Defaults to None.
        conversion (Union[Dict[Union[int, str],Dict[Resource, float]], Dict[Resource, float]], optional): conversion data (Dict[Resource, float]]), if multimode the of form Dict[int,Dict[Resource, float]]. Defaults to None.
        material_cons (Union[Dict[Union[int, str], Dict[Material, float]],Dict[Material, float]], optional): Materials consumed per unit basis of production capacity. Defaults to None.
        land (Union[float, Tuple[float], Theta], optional): land requirement per unit basis. Defaults to None.
        capex (Union[float, dict, Tuple[float], Theta], None): Capital expenditure per unit basis, can be scaled with capacity. Defaults to None.
        fopex (Union[float, Tuple[float], Theta], None): Fixed operational expenditure per unit basis, can be scaled with capacity. Defaults to None.
        vopex (Union[float, Tuple[float], Theta], None): Variable operational expenditure per unit basis, can be scaled with capacity. Defaults to None.
        incidental (Union[float, Tuple[float], Theta], None): Incidental expenditure. Defaults to None.
        gwp (float, optional): global warming potential for settting up facility per unit basis. Defaults to None.
        odp (float, optional): ozone depletion potential for settting up facility per unit basis. Defaults to None.
        acid (float, optional): acidification potential for settting up facility per unit basis. Defaults to None.
        eutt (float, optional): terrestrial eutrophication potential for settting up facility per unit basis. Defaults to None.
        eutf (float, optional): fresh water eutrophication potential for settting up facility per unit basis. Defaults to None.
        eutm (float, optional): marine eutrophication potential for settting up facility per unit basis. Defaults to None.
        introduce (int, optional): Time period in the network scale when introduced. Defaults to None.
        lifetime (float, optional): the expected lifetime of process. Defaults to None.
        retire (int, optional): Time period in the network scale when retired. Defaults to None.
        trl (str, optional): technology readiness level. Defaults to None.
        p_fail (float, optional): failure rate of process. Defaults to None.
        storage(Resource, optional): Resource that can be stored in process. Defaults to None.
        store_max (float, optional): Maximum allowed storage of resource in process. Defaults to None.
        store_min (float, optional): Minimum allowed storage of resource in process. Defaults to None.
        storage_cost: (float, optional): penalty for mainting inventory per time period in the scheduling scale. Defaults to None.
        store_loss: (float, optional): resource loss on the scheduling scale
        block (str, optional): define block for convenience. Defaults to None.
        citation (str, optional): citation for data. Defaults to 'citation needed'.
        label(str, optional):Longer descriptive label if required. Defaults to None
        basis(str, optional): base units for operation. Defaults to 'unit'.
        ctype (List[ProcessType], optional): process type. Defaults to None
        ptype (Dict[ProcessType, ParameterType], optional): paramater type of declared values . Defaults to None
        ltype (List[LocalizeType], optional): which parameters are localized. Defaults to None.


    Examples:
        For processes with varying production capacity

        >>> WF = Process(name='WF', conversion={Wind: -1, Power: 1}, capex= 100, Fopex= 10, Vopex= 1,cap_max=100, gwp=52700, land= 90, basis = 'MW', block='power', label='Wind mill array')

        For process with multiple modes of operation

        >>> PEM = Process(name = 'PEM', conversion = {1: {Power: -1, H2: 19.474, O2: 763.2, H2O: -175.266}, 2: {Power: -1, H2: 1.2*19.474, O2: 1.2*763.2, H2O: 1.2*-175.266}, cap_max= 100, capex = 784000, label = 'PEM Electrolysis')

        For process with multiple resource inputs

        >>> CoolCar = Process(name = 'CoolCar', conversion = {1: {Power: -1, Mile: 1}, 2: {H2: -1, Mile:2}, cap_max= 50, capex = 70, label = 'CoolCar')

    """

    name: str
    cap_max: Union[float, Tuple[float], Theta] = None
    cap_min: Union[float, dict] = None
    conversion: Union[Dict[Union[int, str], Dict[Resource, float]],
                      Dict[Resource, float]] = None
    material_cons: Union[Dict[Union[int, str],
                              Dict[Material, float]], Dict[Material, float]] = None
    land: Union[float, Tuple[float], Theta] = None
    capex: Union[float, dict, Tuple[float], Theta] = None
    fopex: Union[float, Tuple[float], Theta] = None
    vopex: Union[float, Tuple[float], Theta] = None
    incidental: Union[float, Tuple[float], Theta] = None
    gwp: float = None
    odp: float = None
    acid: float = None
    eutt: float = None
    eutf: float = None
    eutm: float = None
    introduce: int = None
    retire: int = None
    lifetime: int = None
    trl: str = None
    p_fail: float = None
    storage: Resource = None
    store_max: float = None
    store_min: float = None
    storage_cost: float = None
    store_loss: float = None
    ctype: List[ProcessType] = None
    ptype: Dict[ProcessType, ParameterType] = None
    ltype: List[LocalizeType] = None
    basis: str = None
    block: str = None
    citation: str = None
    label: str = None
    # depreciated
    varying: list = None
    prod_max: float = None
    prod_min: float = None

    def __post_init__(self):

        if self.ctype is None:
            self.ctype = []

        # *-----------------Set ctype (Component)---------------------------------

        if self.cap_max is not None:
            self.ctype.append(ProcessType.CAPACITY)
            self.ctype.append(ProcessType.CAP_MAX)

        if self.cap_min is not None:
            self.ctype.append(ProcessType.CAP_MIN)

        if self.capex is not None:
            self.ctype.append(ProcessType.CAPEX)
            if isinstance(self.capex, dict):
                self.ctype.append(ProcessType.PWL_CAPEX)
                self.capacity_segments = list(self.capex.keys())
                self.capex_segments = list(self.capex.values())
            else:
                self.ctype.append(ProcessType.LINEAR_CAPEX)

        for i in ['fopex', 'vopex', 'incidental', 'land']:
            if getattr(self, i) is not None:
                getattr(self, 'ctype').append(getattr(ProcessType, i.upper()))

        if self.conversion is not None:
            if get_depth(self.conversion) > 1:
                self.ctype.append(ProcessType.MULTI_PRODMODE)
                self.prod_modes = set(self.conversion.keys())
                self.resource_req = set().union(
                    *[set(self.conversion[i].keys()) for i in self.prod_modes])
            else:
                self.ctype.append(ProcessType.SINGLE_PRODMODE)
                self.resource_req = set(self.conversion.keys())

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

        if self.storage is not None:
            self.ctype.append(ProcessType.STORAGE)
            if self.store_loss is None:
                self.store_loss = 0
            # create a dummy resource if process is storage type.
            self.resource_storage = self.create_storage_resource(
                resource=self.storage, store_max=self.store_max, store_min=self.store_min)
            # efficiency of input to storage is 100 percent
            self.conversion = {self.storage: -1, self.resource_storage: 1}
            self.conversion_discharge = {
                self.resource_storage: -1, self.storage: 1*(1 - self.store_loss)}  # the losses are all at the output (retrival)
            self.resource_req = set(self.conversion.keys())

        # *-----------------Set ptype (Parameter)---------------------------------

        self.ptype = {i: ParameterType.CERTAIN for i in self.ctype}

        if self.cap_max is not None:
            if isinstance(self.cap_max, (tuple, Theta)):
                self.ptype[ProcessType.CAPACITY] = ParameterType.UNCERTAIN
                self.cap_max = create_mpvar(
                    value=self.cap_max, component=self, ptype=MPVarType.CAPACITY)

        for i in ['capex', 'fopex', 'vopex', 'incidental', 'land']:
            if getattr(self, i) is not None:
                if isinstance(getattr(self, i), (tuple, Theta)):
                    self.ptype[getattr(ProcessType, i.upper())
                               ] = ParameterType.UNCERTAIN
                    setattr(self, i, create_mpvar(value=getattr(self, i),
                            component=self, ptype=getattr(MPVarType, i.upper())))

        # *-----------------Set etype (Emission)---------------------------------

        self.etype = []
        self.emissions = dict()
        for i in ['gwp', 'odp', 'acid', 'eutt', 'eutf', 'eutm']:
            if getattr(self, i) is not None:
                self.etype.append(getattr(EmissionType, i.upper()))
                self.emissions[i] = getattr(self, i)

        # *-----------------Factors and Localization dicts ---------------------------------
        self.ltype = {getattr(ProcessType, i.upper()): [] for i in [
            'cap_max', 'cap_min', 'capex', 'fopex', 'vopex', 'incidental'] if getattr(ProcessType, i.upper()) in self.ctype}
        self.param_factors = {getattr(ProcessType, i.upper()): [] for i in [
            'capacity', 'capex', 'fopex', 'vopex', 'incidental'] if getattr(ProcessType, i.upper()) in self.ctype}
        self.localize_factors = {getattr(ProcessType, i.upper()): [] for i in [
            'cap_max', 'cap_min', 'capex', 'fopex', 'vopex', 'incidental'] if getattr(ProcessType, i.upper()) in self.ctype}

        # *----------------- Generate Random Name---------------------------------

        if self.name is None:
            self.name = f'{self.__class__.__name__}_{uuid.uuid4().hex}'

        # *----------------- Warnings---------------------------------

        if self.prod_max is not None:
            warn(
                f'{self.name}: prod_max has been depreciated. Please use cap_max instead')
        if self.prod_min is not None:
            warn(
                f'{self.name}: prod_min has been depreciated. Please use cap_min instead')
        if self.varying is not None:
            warn(f'{self.name}: varying has been depreciated. Variability will be intepreted based on data provided to energiapy.Location')

    def create_storage_resource(self, resource: Resource, store_max: float = None, store_min: float = None) -> Resource:
        """Creates a dummy resource for storage, used if process is storage type

        Args:
            process_name(str): Name of storage process
            resource (Resource): Dummy resource name derived from stored resource
            store_max (float, optional): Maximum amount of resource that can be stored. Defaults to 0.
            store_min (float, optional): Minimum amount of resource that can be stored. Defaults to 0.

        Returns:
            Resource: resource object for storage in process
        """

        return Resource(name=f"{self.name}_{resource.name}_stored", store_loss=self.store_loss, store_max=self.store_max, store_min=self.store_min,
                        label=f'{resource.label}_{self.name}_stored')

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
