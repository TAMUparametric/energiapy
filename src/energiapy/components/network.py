"""energiapy.Network - links Locations through Transports
"""
# TODO - check transport avail (only has transport name) and transport dict (has transport object)

import uuid
from dataclasses import dataclass, field
from itertools import product
from typing import Dict, List, Tuple, Union

from pandas import DataFrame

from .comptype import LocationType, NetworkType, TransportType
from .location import Location
from .parameters.factor import Factor
from .parameters.mpvar import Theta, create_mpvar
from .parameters.paratype import FactorType, MPVarType, ParameterType
from .temporal_scale import TemporalScale
from .transport import Transport


@dataclass
class Network:
    """
    Networks link Locations with Transports
    A distance matrix and Transport matrix needs to be provided

    Args:
        name (str): name of the network. Enter None to randomly assign a name.
        source_locations (List[location], optional): list of location dataclass objects of source locations
        sink_locations (List[location], optional): list of location dataclass objects of sink locations
        distance_matrix (List[List[float]], optional): matrix with distances between sources and sinks, needs to be ordered
        transport_matrix (List[List[float]], optional): matrix with distances between sources and sinks, needs to be ordered
        land_max (Union[float, Tuple[float], Theta], optional): land available. Defaults to None.
        land_max_factor (DataFrame, optional): factor for changing land availability. Defaults to None. 
        capacity_factor (Dict[Tuple[Location, Location], Dict[Transport, DataFrame]], optional):  Factor for varying capacity for Transport between Locations. Defaults to None.
        capex_factor (Dict[Tuple[Location, Location], Dict[Transport, DataFrame]], optional):  Factor for varying capital expenditure for Transport between Locations. Defaults to None.
        vopex_factor (Dict[Tuple[Location, Location], Dict[Transport, DataFrame]], optional):  Factor for varying variable operational expenditure for Transport between Locations. Defaults to None.
        fopex_factor (Dict[Tuple[Location, Location], Dict[Transport, DataFrame]], optional):  Factor for varying fixed operational expenditure for Transport between Locations. Defaults to None.
        incidental_factor (Dict[Tuple[Location, Location], Dict[Transport, DataFrame]], optional):  Factor for varying incidental expenditure for Transport between Locations. Defaults to None.
        citation (str, optional): can provide citations for your data sources. Defaults to None.
        label (str, optional): used while generating plots. Defaults to None.
        ctype (List[LandType], optional): Network type type. Defaults to None.
        ptype (Dict[LandType, ParameterType], optional): paramater type of declared values. Defaults to None.
        ftype (Dict[LandType, FactorType], optional): factor type of declared factors. Defaults to None.

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
    # Primary attributes
    scales: TemporalScale
    source_locations: List[Location] = field(default_factory=list)
    sink_locations: List[Location] = field(default_factory=list)
    distance_matrix: List[List[float]] = field(default_factory=list)
    transport_matrix: List[List[Transport]] = field(default_factory=list)
    # Network parameters
    land_max: Union[float, Tuple[float], Theta] = None
    land_max_factor: DataFrame = None
    # Factors for Transport
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
    # Details
    citation: str = None
    label: str = None
    # Types
    ctype: List[NetworkType] = None
    ptype: Dict[NetworkType, ParameterType] = None
    ftype: Dict[NetworkType, FactorType] = None
    # Depreciated
    capacity_scale_level: int = None
    capex_scale_level: int = None
    vopex_scale_level: int = None
    fopex_scale_level: int = None

    def __post_init__(self):

        # *-------------------------- Update Network Factors and Parameters -----------------

        if self.ctype is None:
            self.ctype = []
        self.ptype, self.ftype = dict(), dict()
        # Currently limited to land_max
        # If MPVar Theta or a tuple is provided as bounds ptype UNCERTAIN
        # if factors are provided a Factor is generated and ftype is updated
        # or else, parameter is treated as CERTAIN parameter
        for i in ['land_max']:
            self.update_network_params_and_factors(i)

        # * ------------------------- Update Locations Factors and Parameters ----------------------

        for i in self.source_locations:
            i.ctype.append(LocationType.SOURCE)
            i.ptype[LocationType.SOURCE] = ParameterType.CERTAIN
        for i in self.sink_locations:
            i.ctype.append(LocationType.SINK)
            i.ptype[LocationType.SINK] = ParameterType.CERTAIN

        # makes dictionary of available transport options between locations
        self.transport_dict = self.make_transport_dict()
        # makes dictionary of distances between locations
        self.distance_dict = self.make_distance_dict()
        # same as transport dict, I do not know why I made two, but now I am too scared to change it
        self.transport_avail_dict = self.make_transport_avail_dict()

        self.locations = list(
            set(self.source_locations).union(set(self.sink_locations)))  # all locations in network

        self.source_sink_resource_dict = self.make_source_sink_resource_dict()

        for i in ['capacity', 'capex', 'fopex', 'vopex', 'incidental']:
            self.update_transport_factors(parameter=i)

        # *----------------- Generate Random Name ------------------------

        if self.name is None:
            self.name = f'{self.__class__.__name__}_{uuid.uuid4().hex}'

        # *----------------- Depreciation Warnings-----------------------------

        if self.capacity_scale_level is not None:
            raise ValueError(
                f'{self.name}: capacity_scale_level is depreciated. scale levels determined from factor data now')

        if self.capex_scale_level is not None:
            raise ValueError(
                f'{self.name}: capex_scale_level is depreciated. scale levels determined from factor data now')

        if self.fopex_scale_level is not None:
            raise ValueError(
                f'{self.name}: fopex_scale_level is depreciated. scale levels determined from factor data now')

        if self.vopex_scale_level is not None:
            raise ValueError(
                f'{self.name}: vopex_scale_level is depreciated. scale levels determined from factor data now')

    # *----------------- Functions-------------------------------------

    def update_network_params_and_factors(self, parameter: str):
        """Updated ctype based on type of parameter provide.
        Creates MPVar if Theta or tuple of bounds
        also updates ftype if factors provides and puts Factor in place of DataFrame

        Args:
            parameter (str): land parameters
        """

        if getattr(self, parameter) is not None:
            # Update ctype
            ctype_ = getattr(NetworkType, parameter.upper())
            self.ctype.append(ctype_)
            # Update ptype
            if isinstance(getattr(self, parameter), (tuple, Theta)):
                self.ptype[ctype_] = ParameterType.UNCERTAIN
                mpvar_ = create_mpvar(value=getattr(
                    self, parameter), component=self, ptype=getattr(MPVarType, f'network_{parameter}'.upper()))
                setattr(self, parameter, mpvar_)
            else:
                self.ptype[ctype_] = ParameterType.CERTAIN

        if getattr(self, f'{parameter}_factor') is not None:
            # Update ftype
            ftype_ = getattr(FactorType, f'network_{parameter}'.upper())
            self.ftype[ctype_] = ftype_
            factor_ = Factor(component=self, data=getattr(
                self, f'{parameter}_factor'), ftype=ftype_, scales=self.scales, location=self)
            setattr(self, f'{parameter}_factor', factor_)

    def update_transport_factors(self, parameter: str):
        """Updates Transport factor data to Factor and updates ftype and factors

        Args:
            parameter (str): Transport parameter factor to update
        """
        if getattr(self, f'{parameter}_factor') is not None:
            for location_tuple, transport_n_data in getattr(self, f'{parameter}_factor').items():
                for transport, data in transport_n_data.items():
                    ctype_ = getattr(TransportType, parameter.upper())
                    ftype_ = getattr(
                        FactorType, f'trans_{parameter}'.upper())
                    factor_ = Factor(component=transport, data=data, ftype=ftype_,
                                     scales=self.scales, location=location_tuple)

                    getattr(self, f'{parameter}_factor')[
                        location_tuple][transport] = factor_

                    if not transport.ftype:
                        transport.ftype[ctype_] = [
                            (location_tuple, ftype_)]
                        transport.factors[ctype_] = [
                            (location_tuple, factor_)]
                    else:
                        if ctype_ in transport.ftype_:
                            transport.ftype[ctype_].append(
                                (location_tuple, ftype_))
                            transport.factors[ctype_].append(
                                (location_tuple, factor_))
                        else:
                            transport.ftype[ctype_] = [
                                (location_tuple, ftype_)]
                            transport.factors[ctype_] = [
                                (location_tuple, factor_)]

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

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
