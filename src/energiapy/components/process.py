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
from typing import Dict, Union
from ..components.resource import Resource
from ..components.material import Material
import pandas
from random import sample

@dataclass
class Process:
    """
    Processes convert resources into other resources 

    Args:
        name (str): name of process, short ones are better to deal with.
        conversion (Dict[resource, float], optional): conversion data. Defaults to None.
        cost (floatordict, optional): cost of operation {'CAPEX':_, 'Fixed O&M':_, 'Variable O&M':_}. Defaults to None.
        material_cons (Dict[material, float], optional): material consumption data. Defaults to None.
        intro_scale (int, optional): scale when process is introduced. Defaults to 0.
        prod_max (float, optional): maximum production. Defaults to 0.
        prod_min (float, optional): minimum production. Defaults to 0.
        cap_seg (dict, optional): capacity pwl segment. Defaults to None.
        capex_seg (dict, optional): capex pwl segment. Defaults to None.
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
    conversion: Dict[Resource, float] = field(default_factory= dict)
    cost: Union[float, dict] = None #field(default_factory = dict) 
    material_cons: Dict[Material, float] = field(default_factory= dict)
    intro_scale: int = 0
    exit_scale: int = 0
    prod_max: float = 0
    prod_min: float = 0.01
    cap_seg: dict = field(default_factory= dict)
    capex_seg: dict = field(default_factory= dict)
    basis: str = 'unit'
    carbon_credit: bool = False
    gwp: tuple = None
    land: float = 0
    trl: str = ''
    block: str = None
    citation: str = 'citation needed'
    lifetime: tuple = None
    varying:bool = False
    p_fail: float = None
    label: str = ''
    storage: list = None

    def __post_init__(self):
        if self.cost is not None:
            self.capex = self.cost['CAPEX']
            self.fopex = self.cost['Fixed O&M']
            self.vopex = self.cost['Variable O&M']            
        else:
            self.capex = 100
            self.fopex = 10
            self.vopex = 1
        # self.capacity_factor = self.make_capacity_factor()

        
         
    def __repr__(self):
        return self.name
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        return self.name == other.name
