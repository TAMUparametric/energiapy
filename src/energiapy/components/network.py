"""Linkage data class  
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
from itertools import product
from ..components.transport import Transport
from ..components.location import Location
from typing import List


@dataclass
class Network:
    """
    Networks link locations with Transports
    
    Args:
        name (str): name of the network, short ones are better to deal with
        source_locations (List[location], optional): list of location dataclass objects of source locations
        sink_locations (List[location], optional): list of location dataclass objects of sink locations
        distance_matrix (List[List[float]], optional): matrix with distances between sources and sinks, needs to be ordered
        transport_matrix (List[List[float]], optional): matrix with distances between sources and sinks, needs to be ordered
        label(str, optional):Longer descriptive label if required. Defaults to ''

    Examples:
        Networks object with to and from movement of resources using Transport. In the following example, Train and Pipeline can be set up from 'Goa' to 'Texas'
        
        >>> Move = Network(name= 'Network', source_locations= [Goa, Texas], sink_locations= [Texas, Goa], distance_matrix= [[0, 500],[500, 0]], transport_matrix= [[], [Train, Pipe]], [[Train, Pipe], []]], label = 'network for moving stuff') 
        
        Networks can also have one way movement of resources. In the following example, a Pipeline is set up from Goa to Texas.
        
        >>> BrainDrain = Network(name= 'BrainDrain, source_locations= [Goa], sink_locations= [Texas], distance_matrix= [[0, 500],[500, 0]], transport_matrix= [[], [Pipe]], [[], []]], label = 'The Pipeline') )
    """
    name: str
    source_locations: List[Location] = field(default_factory=list)
    sink_locations: List[Location] = field(default_factory=list)
    distance_matrix: List[List[float]] = field(default_factory=list)
    transport_matrix: List[List[Transport]] = field(default_factory=list)
    label: str = ''

    def __post_init__(self):
        """Makes handy dictionaries
        
        Args:
            transport_dict (dict): dictionary with transportation modes available between sources and sinks
            distance_dict (dict): dictionary of distances from sources to sinks
            transport_avail_dict (dict): transportation modes available between sources and sinks 
            locations (list): list of locations, sinks + sources 
        """
        self.transport_dict = self.make_transport_dict()
        self.distance_dict = self.make_distance_dict()
        self.transport_avail_dict = self.make_transport_avail_dict()
        self.locations = list(
            set(self.source_locations).union(set(self.sink_locations)))

    def make_distance_dict(self) -> dict:
        """returns a dictionary of distances from sources to sinks

        Returns:
            dict: a dictionary of distances from sources to sinks
        """
        distance_dict = {(self.source_locations[i].name, self.sink_locations[j].name):
                         self.distance_matrix[i][j] for i, j in product(range(len(self.source_locations)), range(len(self.sink_locations)))}
        return distance_dict

    def make_transport_dict(self) -> dict:
        """returns a dictionary of trasportation modes available between sources to sinks

        Returns:
            dict: a dictionary of trasportation modes available between sources to sinks
        """
        transport_dict = {(self.source_locations[i].name, self.sink_locations[j].name):
                          set(self.transport_matrix[i][j]) for i, j in product(range(len(self.source_locations)), range(len(self.sink_locations)))}
        return transport_dict

    def make_transport_avail_dict(self) -> dict:
        """returns a dictionary with transportation modes available between sources and sinks

        Returns:
            dict: a dictionary with transportation modes available between sources and sinks 
        """
        transport_avail_dict = {
            i: {j.name for j in self.transport_dict[i]} for i in self.transport_dict.keys()}
        return transport_avail_dict

    def __refr__(self):
        return self.name
