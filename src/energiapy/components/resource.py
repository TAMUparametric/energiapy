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
        name (str): name of resource, short ones are better to deal with.
        cons_max (float, optional): Maximum allowed resource consumption in time period. Defaults to 0.
        loss (float, optional): Amount of resource lost in time period [h]. Defaults to 0.
        revenue (float, optional): Amount earned through sale of resource [$/unit]. Defaults to 0.
        price (float, optional): Purchase cost of unit [$/unit]. Defaults to 0.
        mile (float, optional): mileage offered by resource [mile/unit]. Defaults to 0.
        store_max (float, optional): Maximum storage capacity increase in a year. Defaults to 0.
        store_min (float, optional): Minimum storage capacity increase in a year. Defaults to 0.
        sell (bool, optional): True if resource can be discharged. Defaults to False.
        demand (bool, optional): True, if the process has to meet set demand. Defaults to False.
        basis (str, optional): Base unit for the resource. Defaults to 'unit'.
        block (str, optional): Assign a block for categorization. Defaults to None.
        citation (str, optional): Add citations for data sources. Defaults to 'citation needed'.
        varying (bool, optional): If the cost of resource is varying/uncertain. Defaults to False.
        label(str, optional): Longer descriptive label if required. Defaults to ''
    """
    
    name: str
    cons_max: float = 0
    loss: float = 0
    revenue: float = 0
    price: float = 0
    mile: float = 0
    store_max: float = 0
    store_min: float = 0
    sell: bool = False
    demand: bool = False
    basis: str = 'unit'
    block: str = None
    citation: str = 'citation needed'
    varying: bool = False
    label: str = ''
    gwp: float = 0
    # def __post_init__(self):
    #     self.cost_factor = self.make_cost_factor()

    def __repr__(self):
        return self.name
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        return self.name == other.name
     
        

# %%

 