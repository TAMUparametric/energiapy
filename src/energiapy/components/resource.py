#%%
"""Resource data class  
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "0.0.1"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from dataclasses import dataclass
import pandas
from enum import Enum, auto


@dataclass
class Resource:
    """
    Object with resource data
    
    Args:
        name (str): Resource ID, long descriptive names can be set with label.
        cons_max (float, optional): Maximum allowed resource consumption in each time period of the scheduling scale. Defaults to 0.
        loss (float, optional): Amount of resource lost in time period of scheduling scale if stored. Defaults to 0.
        revenue (float, optional): Amount earned from sale of resource [$/unit] in each time period of scheduling scale. Defaults to 0.
        price (float, optional): Purchase cost per unit of resource in each time period of scheduling scale [$/unit]. Defaults to 0.
        store_max (float, optional): Maximum allowed storage capacity increase in a year. Defaults to 0.
        store_min (float, optional): Minimum allowed storage capacity increase in a year. Defaults to 0.
        sell (bool, optional): True if resource can be discharged. Defaults to False.
        demand (bool, optional): True, if the process has to meet specific demand. If True, sell defaults to True. Defaults to False.
        basis (str, optional): Unit basis for the resource. Defaults to 'unit'.
        block (str, optional): Assign a block for categorization. Defaults to None.
        citation (str, optional): Add citations for data sources. Defaults to 'citation needed'.
        varying (bool, optional): If the cost of resource is varying/uncertain. Defaults to False.
        label (str, optional): Longer descriptive label if required. Defaults to ''.
        gwp (float, optional): Global Warming Potential per unit consumption of resource. Defaults to 0.and
        
    Examples:
        For a resource that cannot be consumed from outside the system, but can be stored.
        
        >>> Charge = Resource(name= 'Charge', loss= 0.001, store_max= 100, store_min= 5, basis='MW', block= 'energy storage', label='Water', block='Resource')
        
        For a resource that can be consumed from outside the system, and has a varying purchase price.
        
        >>> NG = Resource(name= 'NG', price= 4, basis= 'Btu', varying= True, label= 'Natural Gas', gwp= 20)
        
        For a resource that is produced and needs to meet a fixed demand.
        
        >>> H2 = Resource(name= 'H2', demand= True, basis= 'kg', label= 'Hydrogen')

    """
    
    name: str
    cons_max: float = 0
    loss: float = 0
    revenue: float = 0
    price: float = 0
    store_max: float = 0
    store_min: float = 0
    sell: bool = False
    demand: bool = False
    basis: str = 'unit'
    block: str = ''
    citation: str = 'citation needed'
    varying: bool = False
    label: str = ''
    gwp: float = 0

    def __post_init__(self):
        if self.demand is True:
            self.sell = True
            
    def __repr__(self):
        return self.name
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        return self.name == other.name
     
        

# %%

 