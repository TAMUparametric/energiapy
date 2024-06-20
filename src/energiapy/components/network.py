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
import uuid

from pandas import DataFrame

from .location import Location
from .transport import Transport
from .factor import Factor
from .temporal_scale import TemporalScale
from .comptype import LocationType, TransportType, ParameterType, FactorType
from ..utils.scale_utils import scale_changer
from warnings import warn


@dataclass
class Network:
    """
    Networks link locations with Transports

    Args:
        name (str): name of the network. Enter None to randomly assign a name.
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
    capacity_factor: Dict[Tuple[Location, Location],
                          Dict[Transport, DataFrame]] = None
    capex_factor: Dict[Tuple[Location, Location],
                       Dict[Transport, DataFrame]] = None
    vopex_factor: Dict[Tuple[Location, Location],
                       Dict[Transport, DataFrame]] = None
    fopex_factor: Dict[Tuple[Location, Location],
                       Dict[Transport, DataFrame]] = None
    incidental_factor: Dict[Tuple[Location, Location],
                            Dict[Transport, DataFrame]] = None
    label: str = None

    # depreciated
    capacity_scale_level: int = 0
    capex_scale_level: int = 0
    vopex_scale_level: int = 0
    fopex_scale_level: int = 0

    def __post_init__(self):
        """Makes handy dictionaries

        Args:
            transport_dict (dict): dictionary with transportation modes available between sources and sinks
            distance_dict (dict): dictionary of distances from sources to sinks
            transport_avail_dict (dict): transportation modes available between sources and sinks
            locations (list): list of locations, sinks + sources
        """
        for i in self.source_locations:
            i.ctype.append(LocationType.SOURCE)

        for i in self.sink_locations:
            i.ctype.append(LocationType.SINK)

        self.transport_dict = self.make_transport_dict(
        )  # makes dictionary of available transport options between locations
        # makes dictionary of distances between locations
        self.distance_dict = self.make_distance_dict()
        # same as transport dict, I do not know why I made two, but now I am too scared to change it
        self.transport_avail_dict = self.make_transport_avail_dict()
        self.locations = list(
            set(self.source_locations).union(set(self.sink_locations)))  # all locations in network
        self.source_sink_resource_dict = self.make_source_sink_resource_dict()

        for m in ['capacity', 'capex', 'fopex', 'vopex', 'incidental']:
            if getattr(self, f'{m}_factor') is not None:
                for i, j in getattr(self, f'{m}_factor').items():
                    for k, l in j.items():
                        k.ptype[getattr(TransportType, f'{m}'.upper(
                        ))] = ParameterType.DETERMINISTIC_DATA
                        getattr(self, f'{m}_factor')[i][k] = Factor(
                            component=k, data=l, ctype=FactorType.CAPACITY, scales=self.scales)

        # if self.capacity_factor is not None:
        #     if isinstance(list(self.capacity_factor[list(self.capacity_factor.keys())[0]].values())[0], DataFrame):
        #         self.capacity_factor = {tuple([m.name for m in list(i)]): scale_changer(
        #             j, scales=self.scales, scale_level=self.capacity_scale_level) for i, j in self.capacity_factor.items()}
        #     else:
        #         warn(
        #             'Input should be a dict of a dict of a DataFrame, Dict[Tuple[Location, Location], Dict[Transport, float]]')

        # if self.capex_factor is not None:
        #     if isinstance(list(self.capex_factor[list(self.capex_factor.keys())[0]].values())[0], DataFrame):
        #         self.capex_factor = {(m.name for m in i): scale_changer(
        #             j, scales=self.scales, scale_level=self.capex_scale_level) for i, j in self.capex_factor.items()}
        #     else:
        #         warn(
        #             'Input should be a dict of a dict of a DataFrame, Dict[Tuple[Location, Location], Dict[Transport, float]]')

        # if self.fopex_factor is not None:
        #     if isinstance(list(self.fopex_factor[list(self.fopex_factor.keys())[0]].values())[0], DataFrame):
        #         self.fopex_factor = {i: scale_changer(
        #             j, scales=self.scales, scale_level=self.fopex_scale_level) for i, j in self.fopex_factor.items()}
        #     else:
        #         warn(
        #             'Input should be a dict of a dict of a DataFrame, Dict[Tuple[Location, Location], Dict[Transport, float]]')

        # if self.vopex_factor is not None:
        #     if isinstance(list(self.vopex_factor[list(self.vopex_factor.keys())[0]].values())[0], DataFrame):
        #         self.vopex_factor = {i: scale_changer(
        #             j, scales=self.scales, scale_level=self.vopex_scale_level) for i, j in self.vopex_factor.items()}
        #     else:
        #         warn(
        #             'Input should be a dict of a dict of a DataFrame, Dict[Tuple[Location, Location], Dict[Transport, float]]')

        # if self.incidental_factor is not None:
        #     if isinstance(list(self.incidental_factor[list(self.incidental_factor.keys())[0]].values())[0], DataFrame):
        #         self.incidental_factor = {i: scale_changer(
        #             j, scales=self.scales, scale_level=self.incidental_scale_level) for i, j in self.incidental_factor.items()}
        #     else:
        #         warn(
        #             'Input should be a dict of a dict of a DataFrame, Dict[Tuple[Location, Location], Dict[Transport, float]]')

        if self.name is None:
            self.name = f"Network_{uuid.uuid4().hex}"

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
