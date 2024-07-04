"""energiapy.Process - converts one Resource to another Resource, Or stores Resource  
"""
# TODO - diff between storage_loss and conversion efficiency

import operator
import uuid
from dataclasses import dataclass
from functools import reduce
from typing import Dict, List, Set, Tuple, Union

from pandas import DataFrame

from ..utils.data_utils import get_depth
from .type.process import ProcessType
from .material import Material
from ..parameters.bound import Big, BigM
from ..parameters.factor import Factor
from ..parameters.mpvar import Theta
from ..parameters.parameter import Parameter, Parameters
from ..parameters.conversion import Conversion
from ..parameters.type.property import *
from ..parameters.type.disposition import *
from .temporal_scale import TemporalScale
from .type.resource import ResourceType
from .type.process import ProcessType
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
    capacity: Union[float, bool, 'BigM', List[Union[float, 'BigM']],
                    DataFrame, Tuple[Union[float, DataFrame, Factor]], Theta] = None
    capacity_scale: int = None
    land_use: float = None  # Union[float, Tuple[float], Theta]
    land_use_scale: int = None
    conversion: Union[Dict[Union[int, str], Dict[Resource, float]],
                      Dict[Resource, float]] = None
    material_cons: Union[Dict[Union[int, str],
                              Dict[Material, float]], Dict[Material, float]] = None
    # Expenditure
    capex: Union[float, dict, Tuple[float], Theta] = None
    pwl: dict = None  # piece wise linear capex
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
    pfail: Union[float, Tuple[float], Theta] = None
    # These go to storage_resource defined in STORAGE Process
    # Temporal scale
    # not needed if no deterministic data or parameter scale is provided
    scales: TemporalScale = None
    # LimitType
    discharge: Union[float, bool, 'BigM', List[Union[float, 'BigM']],
                     DataFrame, Tuple[Union[float, DataFrame, Factor]], Theta] = None
    discharge_scale: int = None
    consume: Union[float, bool, 'BigM', List[Union[float, 'BigM']],
                   DataFrame, Tuple[Union[float, DataFrame, Factor]], Theta] = None
    consume_scale: int = None
    store: Union[float, bool, 'BigM', List[Union[float, 'BigM']],
                 DataFrame, Tuple[Union[float, DataFrame, Factor]], Theta] = None
    store_scale: int = None
    # LossType
    store_loss: Union[float, Tuple[float], Theta] = None
    store_loss_scale: int = None
    # CashFlowType
    sell_price: Union[float, Theta, DataFrame,
                      Tuple[Union[float, DataFrame, Factor]]] = None
    purchase_price: Union[float, Theta, DataFrame,
                          Tuple[Union[float, DataFrame, Factor]]] = None
    storage_cost: Union[float, Theta, DataFrame,
                        Tuple[Union[float, DataFrame, Factor]]] = None
    credit: Union[float, Theta, DataFrame,
                  Tuple[Union[float, DataFrame, Factor]]] = None
    penalty: Union[float, Theta, DataFrame,
                   Tuple[Union[float, DataFrame, Factor]]] = None
    # Types
    ctype: List[Union[ProcessType, Dict[ProcessType, Set['Location']]]] = None
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
            self.conversion = Conversion(
                conversion=self.conversion, process=self)
            self.produce = self.conversion.produce
            self.base = self.conversion.base
            self.modes = self.conversion.modes
            self.n_modes = self.conversion.n_modes

            if self.n_modes > 1:
                self.ctype.append(ProcessType.MULTI_PRODMODE)
            elif self.n_modes == 1:
                self.ctype.append(ProcessType.SINGLE_PRODMODE)
            elif self.n_modes == 0:
                self.ctype.append(ProcessType.STORAGE)

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

        # if self.store:
        #     self.ctype.append(ProcessType.STORAGE)
        #     if self.store_loss is None:
        #         self.store_loss = 0
        #     # create a dummy resource if process is storage type.
        #     self.resource_storage = self.create_storage_resource(
        #         resource=self.storage)
        #     # efficiency of input to storage is 100 percent
        #     self.conversion = {self.storage: -1, self.resource_storage: 1}
        #     self.conversion_discharge = {
        #         self.resource_storage: -1, self.storage: 1*(1 - self.store_loss)}  # the losses are all at the output (retrival)
        #     self.resources = set(self.conversion)

        # capex can be linear (LINEAR_CAPEX) or piecewise linear (PWL_CAPEX)
        # if PWL, capex needs to be provide as a dict {capacity_segment: capex_segement}
        if self.pwl:
            self.ctype.append(ProcessType.PWL_CAPEX)
            self.capacity_segments = list(self.pwl)
            self.capex_segments = list(self.pwl.values())
        else:
            self.ctype.append(ProcessType.LINEAR_CAPEX)

        # if any expenditure is incurred
        if any([self.capex, self.fopex, self.vopex, self.incidental]):
            self.ctype.append(ProcessType.EXPENDITURE)

        # if it requires land to set up
        if self.land_use:
            self.ctype.append(ProcessType.LAND)

        # if this process fails
        if self.pfail:
            self.ctype.append(ProcessType.FAILURE)

        # if this process has some readiness aspects defined
        if any([self.introduce, self.retire, self.lifetime]):
            self.ctype.append(ProcessType.READINESS)

        # *-----------------Set ptype (Parameter)---------------------------------
        # ptypes of declared parameters are set to .UNCERTAIN if a MPVar Theta or a tuple of bounds is provided,
        # .CERTAIN otherwise
        # If empty Theta is provided, the bounds default to (0, 1)
        # Factors can be declared at Location (Location, DataFrame), gets converted to  (Location, Factor)

        for i in self.cashflows() + self.emissions() + self.lands() + self.lifes():
            if getattr(self, i.lower()) is not None:
                attr = getattr(self, i.lower())
                if i in self.cashflows():
                    temporal, ptype, psubtype = None, Property.CASHFLOW, getattr(
                        CashFlow, i)
                if i in self.emissions():
                    temporal, ptype, psubtype = None, Property.EMISSION, getattr(
                        Emission, i)
                if i in self.lands():
                    temporal, ptype, psubtype = getattr(
                        self, f'{i.lower()}_scale'), Property.LAND, getattr(Land, i)
                if i in self.lifes():
                    temporal, ptype, psubtype = None, Property.LOSS, getattr(
                        Loss, i)

                param = Parameter(value=attr, ptype=ptype, spatial=SpatialDisp.PROCESS,
                                  temporal=temporal, psubtype=psubtype, component=self, scales=self.scales)
                setattr(self, i.lower(), Parameters(param))

        # *----------------- Update Resource parameters ---------------------------------

        for i in self.process_limits():
            if getattr(self, i.lower()) is not None:
                attr = getattr(self, i.lower())
                temporal, ptype, psubtype = getattr(
                    self, f'{i.lower()}_scale'), Property.LIMIT, getattr(Limit, i)

                param = Parameter(value=attr, ptype=ptype, spatial=SpatialDisp.PROCESS,
                                  temporal=temporal, psubtype=psubtype, component=self.base, declared_at=self, scales=self.scales)
                setattr(self, i.lower(), Parameters(param))

        for i in self.resource_limits() + self.resource_cashflows() + self.resource_losses():
            if getattr(self, i.lower()) is not None:
                attr = getattr(self, i.lower())
                if i in self.resource_limits():
                    temporal, ptype, psubtype = getattr(
                        self, f'{i.lower()}_scale'), Property.LIMIT, getattr(Limit, i)
                if i in self.resource_cashflows():
                    temporal, ptype, psubtype = None, Property.CASHFLOW, getattr(
                        CashFlow, i)
                if i in self.resource_losses():
                    temporal, ptype, psubtype = getattr(
                        self, f'{i.lower()}_scale'), Property.LOSS, getattr(Loss, i)

                param = Parameter(value=attr, ptype=ptype, spatial=SpatialDisp.PROCESS,
                                  temporal=temporal, psubtype=psubtype, component=self.base, declared_at=self, scales=self.scales)
                if getattr(self.base, i.lower()) is not None:
                    getattr(self.base, i.lower()).add(param)
                else:
                    setattr(self.base, i.lower(), Parameters(param))

        # for i in self.process_level_parameters():
        #     self.update_process_parameter(parameter=i)

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

    # *----------------- Class Methods -----------------------------------------
    # * component class types

    @classmethod
    def class_name(cls) -> str:
        """Returns class name 
        """
        return cls.__name__

    @classmethod
    def cashflows(cls) -> List[str]:
        return CashFlow.process()

    @classmethod
    def emissions(cls) -> List[str]:
        return Emission.all()

    @classmethod
    def lands(cls) -> List[str]:
        return Land.process()

    @classmethod
    def lifes(cls) -> List[str]:
        return Life.process()

    @classmethod
    def resource_limits(cls) -> List[str]:
        return Limit.resource()

    @classmethod
    def process_limits(cls) -> List[str]:
        return Limit.process()

    @classmethod
    def resource_cashflows(cls) -> List[str]:
        return CashFlow.resource()

    @classmethod
    def resource_losses(cls) -> List[str]:
        return Loss.resource()

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

    # *----------------- Functions ---------------------------------------------

    # *----------- Hashing --------------------------------

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
