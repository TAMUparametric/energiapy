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


@dataclass
class resource:
    """
    Object with resource data
    """

    def __init__(self, name: str, label: str = '', consumption_max: float = 0, \
        loss: float = 0, revenue: float = 0, varying:bool= False,
                 price: float = 0, mile: float = 0, store_max: float = 0, \
                     store_min: float = 0, sell: bool = False, demand: bool = False, \
                         basis: str = '', block: str = ''):
        """resource object parameters

        Args:
            name (str): ID for the resource
            label (str, optional): name of the resource. Defaults to ''.
            consumption_max (float, optional): Maximum allowed resource consumption in time period [unit/h]. Defaults to 0.
            loss (float, optional): Amount of resource lost in time period [h]. Defaults to 0.
            revenue (float, optional): Amount earned through sale of resource [$/unit]. Defaults to 0.
            varying (bool, optional): If the cost of resource is varying/uncertain. Defaults to False.
            price (float, optional): Purchase cost of unit [$/unit]. Defaults to 0.
            mile (float, optional): mileage offered by resource [mile/unit]. Defaults to 0.
            store_max (float, optional): Maximum storage capacity increase in a year. Defaults to 0.
            store_min (float, optional): Minimum storage capacity increase in a year. Defaults to 0.
            sell (bool, optional): True if resource can be discharged. Defaults to False.
            demand (bool, optional): True, if the process has to meet set demand. Defaults to False.
            basis (str, optional): Base unit for the resource. Defaults to ''.

        """
        self.name = name
        self.label = label
        self.consumption_max = consumption_max
        self.loss = loss
        self.revenue = revenue
        self.price = price
        self.mile = mile
        self.store_max = store_max
        self.store_min = store_min
        self.sell = sell
        self.demand = demand
        self.basis = basis
        self.block = block
        self.varying = varying

    def __repr__(self):
        return self.name
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        return self.name == other.name
        

# %%
