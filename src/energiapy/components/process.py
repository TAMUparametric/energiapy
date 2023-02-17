#%%
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
from ..utils.model_utils import create_dummy_resource
import pandas
from random import sample
from enum import Enum, auto

class Costdynamics(Enum):
    constant = auto()
    pwl = auto()
    scaled = auto()
    wind = auto () #TODO allow user to give equation
    battery = auto () #TODO allow user to give equation
    solar = auto()
    
class ProcessMode(Enum):
    single = auto() #only allows one mode
    multi = auto() # allows multiple modes

@dataclass
class Process:
    """
    Processes convert resources into other resources 

    Args:
        name (str): name of process, short ones are better to deal with.
        conversion (Dict[resource, float], optional): conversion data. Defaults to None.
        cost (floatordict, optional): cost of operation {'CAPEX':_, 'Fixed O&M':_, 'Variable O&M':_}. Defaults to None.
        battery_cost (floatordict, optional): battery sizing cost {'CAPEX_capacity':_, 'CAPEX_power':_,}. Defaults to None
        material_cons (Dict[material, float], optional): material consumption data. Defaults to None.
        intro_scale (int, optional): scale when process is introduced. Defaults to 0.
        prod_max (float, optional): maximum production. Defaults to 0.
        prod_min (float, optional): minimum production. Defaults to 0.
        scaling_segments (dict, optional): capacity and capex pwl segment {'capacity': {1:_, 2:_, ..}, 'capex': {1:_, 2:_, ..}}.Defaults to None.
        capex_seg (dict, optional): capex pwl segment. Defaults to None.
        scaling_metrics (dict, optional): scaling metrics for expenditure {'factor':_, 'ref_capacity':_}. Defaults to None.
        carbon_credit (bool, optional): does process earn carbon credits. Defaults to False.
        basis(str, optional): base units for operation. Defaults to 'unit'.
        gwp (float, optional): global warming potential per basis. Defaults to 0.
        land (float, optional): land requirement. Defaults to 0.
        trl (str, optional): technology readiness level. Defaults to None.
        block (str, optional): define block for convenience. Defaults to None.
        citation (str, optional): citation for data. Defaults to 'citation needed'.
        lifetime (float, optional): the lifetime of process. Defaults to None.
        varying (bool, optional): whether process is subject to uncertainty. Defaults to False.
        p_fail (float, optional): failure rate of process. Defaults to None.
        label(str, optional):Longer descriptive label if required. Defaults to ''
        storage(list, optional): List of Resources that can be stored in process.
    """

    name: str 
    conversion: Dict[Resource, float] = None # field(default_factory= dict)
    # cost: Union[float, dict] = None #field(default_factory = dict) 
    capex: float = None
    fopex: float = None
    vopex: float = None
    incidental: float = None
    material_cons: Dict[Material, float] = None # field(default_factory= dict)
    intro_scale: int = 0
    exit_scale: int = 0
    prod_max: float = 0
    prod_min: float = 0.01
    scaling_segments: dict = field(default_factory= dict)
    scaling_metrics: dict = field(default_factory= dict)
    basis: str = 'unit'
    carbon_credit: bool = False
    gwp: float  = 0
    land: float = 0
    trl: str = ''
    block: str = None
    citation: str = 'citation needed'
    lifetime: tuple = None
    varying:bool = False
    p_fail: float = None
    label: str = ''
    storage: Resource = None
    storage_loss: float = 0
    costdynamics: Costdynamics = Costdynamics.constant
    multiconversion: Dict[int,Dict[Resource, float]] = None 
    
    # if costdynamics is Costdynamics.wind_equation:
    #     cost
        
    # if costdynamics is Costdynamics.battery_equation:
    #     cost

    def __post_init__(self):
        
        if self.multiconversion is not None:
            self.processmode = ProcessMode.multi
        else:
            self.processmode = ProcessMode.single
            
        # self.capacity_factor = self.make_capacity_factor()
        if self.storage is not None:
            # self.storage_dummy = {create_dummy_resource(resource=i, store_max= self.prod_max,\
            #     store_min= self.prod_min) for i in self.storage}
            self.dummy = create_dummy_resource(resource=self.storage, store_max= self.prod_max,store_min= self.prod_min)
            self.conversion = {self.storage:-1, self.dummy:1}
            self.conversion_discharge = {self.dummy:-1, self.storage:1*(1- self.storage_loss)}
        else:
            self.conversion_discharge = None
            self.dummy = None
            
        if self.costdynamics is Costdynamics.constant:
            if self.cost is not None:
                self.capex = self.cost['CAPEX']
                self.fopex = self.cost['Fixed O&M']
                self.vopex = self.cost['Variable O&M'] 
                self.incidental = None
                self.capex_capacity = None
                self.capex_power = None
                           
            else:
                self.capex = 100
                self.fopex = 10
                self.vopex = 1
                self.incidental = None
                self.capex_capacity = None
                self.capex_power = None
                
        if self.costdynamics is Costdynamics.battery:
            if 'CAPEX_capacity' in self.cost.keys():
                self.capex_capacity = self.cost['CAPEX_capacity']
            if 'CAPEX_power' in self.cost.keys():
                self.capex_power = self.cost['CAPEX_power']
            self.capex = None
            self.fopex = None
            self.vopex = None
            self.incidental = None
            
        if self.costdynamics is Costdynamics.wind:
            if 'CAPEX' in self.cost.keys():
                self.capex = self.cost['CAPEX']
            if 'Incidental' in self.cost.keys():
                self.incidental = self.cost['Incidental']
            self.fopex = None
            self.vopex = None
            self.capex_capacity = None
            self.capex_power = None
                
        if self.costdynamics is Costdynamics.solar:
            if 'CAPEX' in self.cost.keys():
                self.capex = self.cost['CAPEX']
            if 'Incidental' in self.cost.keys():
                self.incidental = self.cost['Incidental']
            self.fopex = None
            self.vopex = None
            self.capex_capacity = None
            self.capex_power = None
            
        elif self.costdynamics is Costdynamics.pwl:
            self.capacity_segments = self.scaling_segments['capacity']
            self.capex_segments = self.capex_segments['capex']
            self.capex = None
            self.fopex = None
            self.vopex = None
            
                 
        elif self.costdynamics is Costdynamics.scaled:
            self.scaling_factor = self.scaling_metrics['factor']
            self.ref_capacity = self.scaling_metrics['ref_capacity']
            self.capex = None
            self.fopex = None
            self.vopex = None
            
            
    def __repr__(self):
        return self.name
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        return self.name == other.name
