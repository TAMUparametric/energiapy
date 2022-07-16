"""Cost scenario data class  
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
from ..components.network import Network
from ..components.temporal_scale import Temporal_scale
from ..model.pyomo_cons import *

@dataclass
class Scenario:
    """creates a scenario dataclass object
    Args:
        name (str): ID
        network (network): network object with the locations, transport linakges, and processes (with resources and materials)
        scales (temporal_scale): scales of the problem 
        expenditure_scale_level (int, optional): scale for resource purchase. Defaults to 0.
        scheduling_scale_level (int, optional): scale of production and inventory scheduling. Defaults to 0.
        network_scale_level (int, optional): scale for network decisions such as facility location. Defaults to 0.
        label (str, optional): descriptive label. Defaults to ''.
    """
    name: str 
    network: Network
    scales: Temporal_scale 
    expenditure_scale_level: int = 0
    scheduling_scale_level: int = 0
    network_scale_level: int = 0
    label: str = ''

    def __post_init__(self):    
        self.transport_set = set().union(*self.network.transport_dict.values())
        self.source_locations = self.network.source_locations
        self.sink_locations = self.network.sink_locations
        self.location_set = set(self.source_locations + self.sink_locations)         
        self.process_set = set().union(*[i.processes for i in self.location_set if i.processes is not None])
        self.resource_set = set().union(*[i.resources for i in self.location_set if i.resources is not None])
        self.material_set = set().union(*[i.materials for i in self.location_set if i.materials is not None])
    def __repr__(self):
        return self.name
    


    

    
    