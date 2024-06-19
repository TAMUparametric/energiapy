"""energiapy.Process - converts one Resource to another Resource, Or stores Resource  
"""
from dataclasses import dataclass
from typing import Dict, Union, List, Tuple
from warnings import warn
import uuid
from .material import Material
from .resource import Resource
from .comptype import ParameterType, Th, ProcessRamp, ProcessType, ResourceType
from ..utils.data_utils import get_depth


@dataclass
class Process:
    """
    Processes convert resources into other resources

    Args:
        name (str): name of process, short ones are better to deal with.
        conversion (Union[Dict[Union[int, str],Dict[Resource, float]], Dict[Resource, float]], optional): conversion data (Dict[Resource, float]]), if multimode the of form Dict[int,Dict[Resource, float]]. Defaults to None.
        introduce (int, optional): Time period in the network scale when introduced. Defaults to 0.
        retire (int, optional): Time period in the network scale when retired. Defaults to None.
        capex (Union[float, dict], None): Capital expenditure per unit basis, can be scaled with capacity. Defaults to None.
        fopex (Union[float, dict], None): Fixed operational expenditure per unit basis, can be scaled with capacity. Defaults to None.
        vopex (Union[float, dict], None): Variable operational expenditure per unit basis, can be scaled with capacity. Defaults to None.
        incidental (float, None): Incidental expenditure. Defaults to None.
        material_cons (Union[Dict[Union[int, str], Dict[Material, float]],Dict[Material, float]], optional): Materials consumed per unit basis of production capacity. Defaults to None.
        cap_max (float, optional): Maximum production capacity allowed in a time period of the scheduling scale. Defaults to 0.
        cap_min (float, optional): Minimum production capacity allowed in a time period of the scheduling scale. Defaults to 0.
        credit (float, None): credit earned per unit basis of production. Defaults to None.
        basis(str, optional): base units for operation. Defaults to 'unit'.
        gwp (float, optional): global warming potential for settting up facility per unit basis. Defaults to 0.
        odp (float, optional): ozone depletion potential for settting up facility per unit basis. Defaults to 0.
        acid (float, optional): acidification potential for settting up facility per unit basis. Defaults to 0.
        eutt (float, optional): terrestrial eutrophication potential for settting up facility per unit basis. Defaults to 0.
        eutf (float, optional): fresh water eutrophication potential for settting up facility per unit basis. Defaults to 0.
        eutm (float, optional): marine eutrophication potential for settting up facility per unit basis. Defaults to 0.
        land (float, optional): land requirement per unit basis. Defaults to 0.
        trl (str, optional): technology readiness level. Defaults to None.
        block (str, optional): define block for convenience. Defaults to None.
        citation (str, optional): citation for data. Defaults to 'citation needed'.
        lifetime (float, optional): the expected lifetime of process. Defaults to None.
        varying (VaryingProcess, optional): whether process is subject to uncertainty. Defaults to False.
        p_fail (float, optional): failure rate of process. Defaults to None.
        label(str, optional):Longer descriptive label if required. Defaults to ''
        storage(list, optional): Resource that can be stored in process.
        store_max (float, optional): Maximum allowed storage of resource in process. Defaults to 0.
        store_min (float, optional): Minimum allowed storage of resource in process. Defaults to 0.
        rate_max (Union[Dict[int, float], float]): maximum ramping rates 
        varying_bounds (float, optional): bounds for the variability. Defaults to (0,1).
        mode_ramp (Dict[tuple, int], optional): ramping rates between mode switches. Defaults to None.
        storage_cost: (float, optional). penalty for mainting inventory per time period in the scheduling scale. Defaults to 0.

    Examples:
        For processes with varying production capacity

        >>> WF = Process(name='WF', conversion={Wind: -1, Power: 1}, capex= 100, Fopex= 10, Vopex= 1,cap_max=100, gwp=52700, land= 90, basis = 'MW', block='power', label='Wind mill array')

        For process with multiple modes of operation

        >>> PEM = Process(name = 'PEM', conversion = {1: {Power: -1, H2: 19.474, O2: 763.2, H2O: -175.266}, 2: {Power: -1, H2: 1.2*19.474, O2: 1.2*763.2, H2O: 1.2*-175.266}, cap_max= 100, capex = 784000, label = 'PEM Electrolysis')

        For process with multiple resource inputs

        >>> CoolCar = Process(name = 'CoolCar', conversion = {1: {Power: -1, Mile: 1}, 2: {H2: -1, Mile:2}, cap_max= 50, capex = 70, label = 'CoolCar')

    """

    name: str = None
    introduce: int = None
    retire: int = None
    conversion: Union[Dict[Union[int, str], Dict[Resource, float]],
                      Dict[Resource, float]] = None
    capex: Union[float, dict] = None
    fopex: float = None
    vopex: float = None
    incidental: float = None
    storage_cost: float = None
    land: float = None
    material_cons: Union[Dict[Union[int, str],
                              Dict[Material, float]], Dict[Material, float]] = None
    cap_max: float = None
    cap_min: float = None
    basis: str = None
    gwp: float = None
    odp: float = None
    acid: float = None
    eutt: float = None
    eutf: float = None
    eutm: float = None
    trl: str = None
    block: str = None
    citation: str = None
    lifetime: int = None
    p_fail: float = None
    label: str = None
    storage: Resource = None
    store_loss: float = None
    store_max: float = None
    store_min: float = None
    ctype: List[ProcessType] = None
    ptype: List[ParameterType] = None

    def __post_init__(self):
        """Determines the ProcessMode, CostDynamics, and kicks out dummy resources if process is stores resource

        Args:
            processmode (ProcessMode): Determines whether the model is single mode, multi mode, or storage type.
            resource_storage (Resource):  Dummy resource which is stored in the Process.
            conversion_discharge (Dict[Resource, float]): Creates a dictionary with the discharge conversion values (considers storage loss).
            cost_dynamics (CostDynamics): Determines whether the cost scales linearly with the unit capacity, or is a piecewise-linear function.
        """
        if self.ctype is None:
            self.ctype = []

        if self.ptype is None:
            self.ptype = []

        if self.capex is not None:
            self.ctype.append(ProcessType.EXPENDITURE)
            if isinstance(self.capex, dict):
                self.ctype.append(ProcessType.PWL_CAPEX)
                self.capacity_segments = list(self.capex.keys())
                self.capex_segments = list(self.capex.values())
            else:
                self.ctype.append(ProcessType.LINEAR_CAPEX)

        if self.cap_max is not None:
            self.ctype.append(ProcessType.CAPACITY)

        if self.conversion is not None:
            if get_depth(self.conversion) > 1:
                self.ctype.append(ProcessType.MULTI_PRODMODE)
                self.prod_modes = set(self.conversion.keys())
                self.resource_req = set.union(
                    *[set(self.conversion[i].keys()) for i in self.prod_modes])
            else:
                self.ctype.append(ProcessType.SINGLE_PRODMODE)
                self.resource_req = set(self.conversion.keys())

        if self.material_cons is not None:
            if isinstance(self.material_cons, dict):
                self.ctype.append(ProcessType.HAS_MATMODE)
                self.material_modes = set(self.material_cons.keys())
                self.material_req = set.union(
                    *[set(self.material_cons[i].keys()) for i in self.material_modes])

        else:
            self.ctype.append(ProcessType.NO_MATMODE)

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

        self.emission_potentials_dict = {'gwp': self.gwp, 'odp': self.odp,
                                         'acid': self.acid, 'eutt': self.eutt, 'eutf': self.eutf, 'eutm': self.eutm}

        if self.name is None:
            self.name = f"Process_{uuid.uuid4().hex}"

    def create_storage_resource(self, resource: Resource, store_max: float = 0, store_min: float = 0) -> Resource:
        """Creates a dummy resource for storage, used if process is storage type

        Args:
            process_name(str): Name of storage process
            resource (Resource): Dummy resource name derived from stored resource
            store_max (float, optional): Maximum amount of resource that can be stored. Defaults to 0.
            store_min (float, optional): Minimum amount of resource that can be stored. Defaults to 0.\

        Returns:
            Resource: resource object for storage in process
        """

        return Resource(name=f"{self.name}_{resource.name}_stored", store_loss=resource.store_loss, store_max=store_max, store_min=store_min,
                        basis=resource.basis, block=resource.block, label=resource.label+f"{self.name}(stored)", ctype=[ResourceType.STORE])

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
