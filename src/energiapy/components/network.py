"""Network data class
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2023, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "MIT"
__version__ = "1.1.0"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from dataclasses import dataclass, field
from itertools import product
from typing import List, Dict, Union, Tuple

from pandas import DataFrame

from ..components.location import Location
from ..components.transport import Transport
from ..components.temporal_scale import TemporalScale
from ..utils.scale_utils import scale_changer
from warnings import warn


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

        >>> BrainDrain = Network(name= 'BrainDrain', source_locations= [Goa], sink_locations= [Texas], distance_matrix= [[0, 500],[500, 0]], transport_matrix= [[], [Pipe]], [[], []]], label = 'The Pipeline') )

        Declaring distance matrix: 
        Consider a source (Goa), and two sinks (Texas, Macedonia) at a distance of 1000 and 500 units. The source will form the rows and sinks the columns. 
        The distance matrix will look something like this:

        >>> distance_matrix = [[1000, 500]]

        Declaring transport matrix:
        Similarly say, there is a ship (Ship) avaiable between only Goa and Macedonia, and a flight (Plane) available from Goa to both regions. 
        The transport matrix can be stated as:

        >>> transport_matrix = [[[Ship], [Ship, Plane]]]
    """
    name: str
    scales: TemporalScale
    source_locations: List[Location] = field(default_factory=list)
    sink_locations: List[Location] = field(default_factory=list)
    distance_matrix: List[List[float]] = field(default_factory=list)
    transport_matrix: List[List[Transport]] = field(default_factory=list)
    transport_capacity_factor: Union[float,
                                     Dict[Tuple[Location, Location], Dict[Transport, float]]] = None
    transport_capex_factor: Union[float, Dict[Tuple[Location,
                                                    Location], Dict[Transport, float]]] = None
    transport_vopex_factor: Union[float, Dict[Tuple[Location,
                                                    Location], Dict[Transport, float]]] = None
    transport_fopex_factor: Union[float, Dict[Tuple[Location,
                                                    Location], Dict[Transport, float]]] = None
    transport_capacity_scale_level: int = 0
    transport_capex_scale_level: int = 0
    transport_vopex_scale_level: int = 0
    transport_fopex_scale_level: int = 0

    label: str = ''

    def __post_init__(self):
        """Makes handy dictionaries

        Args:
            transport_dict (dict): dictionary with transportation modes available between sources and sinks
            distance_dict (dict): dictionary of distances from sources to sinks
            transport_avail_dict (dict): transportation modes available between sources and sinks
            locations (list): list of locations, sinks + sources
        """
        self.transport_dict = self.make_transport_dict(
        )  # makes dictionary of available transport options between locations
        # makes dictionary of distances between locations
        self.distance_dict = self.make_distance_dict()
        # same as transport dict, I do not know why I made two, but now I am too scared to change it
        self.transport_avail_dict = self.make_transport_avail_dict()
        self.locations = list(
            set(self.source_locations).union(set(self.sink_locations)))  # all locations in network
        self.source_sink_resource_dict = self.make_source_sink_resource_dict()

        if self.transport_capacity_factor is not None:
            if isinstance(list(self.transport_capacity_factor[list(self.transport_capacity_factor.keys())[0]].values())[0], DataFrame):
                self.transport_capacity_factor = {tuple([m.name for m in list(i)]): scale_changer(
                    j, scales=self.scales, scale_level=self.transport_capacity_scale_level) for i, j in self.transport_capacity_factor.items()}
            else:
                warn(
                    'Input should be a dict of a dict of a DataFrame, Dict[Tuple[Location, Location], Dict[Transport, float]]')

        if self.transport_capex_factor is not None:
            if isinstance(list(self.transport_capex_factor[list(self.transport_capex_factor.keys())[0]].values())[0], DataFrame):
                self.transport_capex_factor = {(m.name for m in i): scale_changer(
                    j, scales=self.scales, scale_level=self.transport_capex_scale_level) for i, j in self.transport_capex_factor.items()}
            else:
                warn(
                    'Input should be a dict of a dict of a DataFrame, Dict[Tuple[Location, Location], Dict[Transport, float]]')

        if self.transport_fopex_factor is not None:
            if isinstance(list(self.transport_fopex_factor[list(self.transport_fopex_factor.keys())[0]].values())[0], DataFrame):
                self.transport_fopex_factor = {i: scale_changer(
                    j, scales=self.scales, scale_level=self.transport_fopex_scale_level) for i, j in self.transport_fopex_factor.items()}
            else:
                warn(
                    'Input should be a dict of a dict of a DataFrame, Dict[Tuple[Location, Location], Dict[Transport, float]]')

        if self.transport_vopex_factor is not None:
            if isinstance(list(self.transport_vopex_factor[list(self.transport_vopex_factor.keys())[0]].values())[0], DataFrame):
                self.transport_vopex_factor = {i: scale_changer(
                    j, scales=self.scales, scale_level=self.transport_vopex_scale_level) for i, j in self.transport_vopex_factor.items()}
            else:
                warn(
                    'Input should be a dict of a dict of a DataFrame, Dict[Tuple[Location, Location], Dict[Transport, float]]')

    def make_distance_dict(self) -> dict:
        """returns a dictionary of distances from sources to sinks

        Returns:
            dict: a dictionary of distances from sources to sinks
        """
        distance_dict = {(self.source_locations[i].name, self.sink_locations[j].name):
                         self.distance_matrix[i][j] for i, j in
                         product(range(len(self.source_locations)), range(len(self.sink_locations)))}
        return distance_dict

    def make_transport_dict(self) -> dict:
        """returns a dictionary of transportation modes available between sources to sinks

        Returns:
            dict: a dictionary of transportation modes available between sources to sinks
        """
        transport_dict = {(self.source_locations[i].name, self.sink_locations[j].name):
                          set(self.transport_matrix[i][j]) for i, j in
                          product(range(len(self.source_locations)), range(len(self.sink_locations)))}
        return transport_dict

    def make_transport_avail_dict(self) -> dict:
        """returns a dictionary with transportation modes available between sources and sinks

        Returns:
            dict: a dictionary with transportation modes available between sources and sinks
        """
        transport_avail_dict = {
            i: {j.name for j in self.transport_dict[i]} for i in self.transport_dict.keys()}
        return transport_avail_dict

    def make_source_sink_resource_dict(self) -> dict:

        source_sink_resource_dict = {
            i: None for i in self.transport_dict.keys()}
        for i in self.transport_dict.keys():
            resources = set()
            for j in self.transport_dict[i]:
                resources = resources.union({k.name for k in j.resources})
            source_sink_resource_dict[i] = resources
        return source_sink_resource_dict

    def __repr__(self):
        return self.name
