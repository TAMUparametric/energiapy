"""Process data class  
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "0.0.1"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from dataclasses import dataclass, field
from typing import Dict, Union, Set
from ..components.resource import Resource
from ..components.material import Material
from ..utils.resource_utils import create_storage_resource
import pandas
from random import sample
from enum import Enum, auto
from warnings import warn


class CostDynamics(Enum):
    constant = auto()
    pwl = auto()

    
class ProcessMode(Enum):
    single = auto() #only allows one mode
    multi = auto() # allows multiple modes
    storage = auto()

class VaryingProcess(Enum):
    deterministic_capacity = auto() #if capacity is uncertain
    uncertain_capacity = auto()
    
@dataclass
class Process:
    """
    Processes convert resources into other resources 

    Args:
        name (str): name of process, short ones are better to deal with.
        conversion (Union[Dict[int,Dict[Resource, float]], Dict[Resource, float]], optional): conversion data (Dict[Resource, float]]), if multimode the of form Dict[int,Dict[Resource, float]]. Defaults to None.
        introduce (int, optional): Time period in the network scale when introduced. Defaults to 0.
        retire (int, optional): Time period in the network scale when retired. Defaults to None.
        capex (Union[float, dict], None): Capital expenditure per unit basis, can be scaled with capacity. Defaults to None.
        fopex (Union[float, dict], None): Fixed operational expenditure per unit basis, can be scaled with capacity. Defaults to None.
        vopex (Union[float, dict], None): Variable operational expenditure per unit basis, can be scaled with capacity. Defaults to None.
        incidental (float, None): Incidental expenditure. Defaults to None.
        material_cons (Dict[Material, float], optional): Materials consumed per unit basis of production capacity. Defaults to None.
        prod_max (float, optional): Maximum production capacity allowed in a time period of the scheduling scale. Defaults to 0.
        prod_min (float, optional): Minimum production capacity allowed in a time period of the scheduling scale. Defaults to 0.
        carbon_credit (float, optional): Carbon Credit earned per unit basis of production. Defaults to 0.
        basis(str, optional): base units for operation. Defaults to 'unit'.
        gwp (float, optional): global warming potential for settting up facility per unit basis. Defaults to 0.
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
        
    Examples:
        For processes with varying production capacity
        
        >>> WF = Process(name='WF', conversion={Wind: -1, Power: 1}, capex= 100, Fopex= 10, Vopex= 1,prod_max=100, gwp=52700, land= 90, basis = 'MW', block='power', label='Wind mill array')

        For process with multiple modes of operation
        
        >>> PEM = Process(name = 'PEM', conversion = {1: {Power: -1, H2: 19.474, O2: 763.2, H2O: -175.266}, 2: {Power: -1, H2: 1.2*19.474, O2: 1.2*763.2, H2O: 1.2*-175.266}, prod_max= 100, capex = 784000, label = 'PEM Electrolysis')
        
        For process with multiple resource inputs
        
        >>> CoolCar = Process(name = 'CoolCar', conversion = {1: {Power: -1, Mile: 1}, 2: {H2: -1, Mile:2}, prod_max= 50, capex = 70, label = 'CoolCar')
        
    """

    name: str 
    introduce: int = 0
    retire: int = None
    conversion: Union[Dict[int,Dict[Resource, float]], Dict[Resource, float]] = None
    capex: Union[float, dict] = None
    fopex: Union[float, dict] = None
    vopex: Union[float, dict] = None
    incidental: float = None
    material_cons: Dict[Material, float] = None
    prod_max: Union[Dict[int,float], float] = 0
    prod_min: float = 0
    basis: str = 'unit'
    carbon_credit: float = 0
    gwp: float  = 0
    land: float = 0
    trl: str = None
    block: str = ''
    citation: str = 'citation needed'
    lifetime: int = None
    varying: VaryingProcess = None
    p_fail: float = None
    label: str = ''
    storage: Resource = None
    storage_loss: float = 0
    store_max: float = 0
    store_min: float = 0

    
    
    def __post_init__(self):
        """Determines the ProcessMode, CostDynamics, and kicks out dummy resources if process is stores resource
        
        Args:
            processmode (ProcessMode): Determines whether the model is single mode, multi mode, or storage type.
            resource_storage (Resource):  Dummy resource which is stored in the Process. 
            conversion_discharge (Dict[Resource, float]): Creates a dictionary with the discharge conversion values (considers storage loss).
            cost_dynamics (CostDynamics): Determines whether the cost scales linearly with the unit capacity, or is a piecewise-linear function.
        """

        if self.storage is not None:
            self.resource_storage= create_storage_resource(process_name= self.name, resource= self.storage, store_max= self.store_max, store_min= self.store_min)
            self.conversion = {self.storage:-1, self.resource_storage:1}
            self.conversion_discharge = {self.resource_storage:-1, self.storage:1*(1- self.storage_loss)}
            self.processmode = ProcessMode.storage
            
        else:
            self.conversion_discharge = None
            self.resource_storage = None
            if type(list(self.conversion.keys())[0]) is int:
                self.processmode = ProcessMode.multi
            else:
                self.processmode = ProcessMode.single
                
        if type(self.capex) is dict:
            self.cost_dynamics = CostDynamics.pwl
        else:
            self.cost_dynamics = CostDynamics.constant      
        
        if self.processmode is ProcessMode.multi:
            self.resource_req = {i.name for i in self.conversion[list(self.conversion.keys())[0]].keys()}
        else:
            self.resource_req = {i.name for i in self.conversion.keys()}     
    
        if self.processmode == ProcessMode.multi:    
            if list(self.prod_max.keys()) != list(self.conversion.keys()):
                warn('The keys for prod_max and conversion need to match if ProcessMode.multi')
                            
    def __repr__(self):
        return self.name
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        return self.name == other.name
