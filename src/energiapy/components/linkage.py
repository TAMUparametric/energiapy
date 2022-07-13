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


from dataclasses import dataclass
from itertools import product
from ..components.transport import transport
from ..components.location import location
from typing import List

@dataclass
class linkage:
    """Object with data regarding the linakges between two locations
    """
    
    def __init__(self, name:str, source_locations:List[location], sink_locations:List[location], distance_matrix:List[list],\
        transport_matrix:List[List[transport]]= None, label:str= ''):
        """creates a dataclass with information regarding the linakges between sources and sinks
        including - the distances and available transport modes

        Args:
            name (str): _description_
            source_locations (List[location]): list of location dataclass objects of source locations
            sink_locations (List[location]): list of location dataclass objects of sink locations
            distance_matrix (List[list]): matrix with distances between sources and sinks, needs to be ordered
            label (str, optional): label. Defaults to ''.
        """
        self.name = name
        self.source_locations = source_locations
        self.sink_locations = sink_locations
        self.distance_matrix = distance_matrix
        self.distance_dict = self.make_distance_dict()
        self.transport_matrix = transport_matrix
        self.transport_dict = self.make_transport_dict()
        self.label = label 
        
    def make_distance_dict(self) -> dict:
        """returns a dictionary of distances from sources to sinks

        Returns:
            dict: a dictionary of distances from sources to sinks
        """
        distance_dict = {(self.source_locations[i].name, self.sink_locations[j].name): \
            self.distance_matrix[i][j] for i,j in product(range(len(self.source_locations)), range(len(self.sink_locations)))}
        return distance_dict
    
    def make_transport_dict(self) -> dict:
        """returns a dictionary of trasportation modes available between sources to sinks

        Returns:
            dict: a dictionary of trasportation modes available between sources to sinks
        """
        transport_dict = {(self.source_locations[i].name, self.sink_locations[j].name): \
            self.transport_matrix[i][j] for i,j in product(range(len(self.source_locations)), range(len(self.sink_locations)))}
        return transport_dict
    
    def __refr__(self):
        return self.name
    
    
    