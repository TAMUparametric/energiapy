"""energiapy.Network - links Locations through Transports
"""
# TODO - check transport avail (only has transport name) and transport dict (has transport object)
# TODO - add CAP_MAX and TRANS_LOSS factors for Transport
# TODO - do we need transport_avail_dict???

from dataclasses import dataclass, field


@dataclass
class Network:
    pass

    # name: str
    # # Primary attributes
    # scales: Scale
    # sources: List[Location]
    # sinks: List[Location]
    # distance_matrix: List[List[float]]
    # transport_matrix: List[List[Transport]]
    # land_max: Union[float, Tuple[float], Theta, bool, 'Big'] = None
    # land_max_factor: DataFrame = None
    # # Factors for Transport
    # cap_max_factor: Dict[Tuple[Location, Location],
    #                      Dict[Transport, DataFrame]] = None
    # capacity_factor: Dict[Tuple[Location, Location],
    #                       Dict[Transport, DataFrame]] = None
    # capex_factor: Dict[Tuple[Location, Location],
    #                    Dict[Transport, DataFrame]] = None
    # vopex_factor: Dict[Tuple[Location, Location],
    #                    Dict[Transport, DataFrame]] = None
    # fopex_factor: Dict[Tuple[Location, Location],
    #                    Dict[Transport, DataFrame]] = None
    # incidental_factor: Dict[Tuple[Location, Location],
    #                         Dict[Transport, DataFrame]] = None
    # # Details
    # basis: str = None
    # label: str = None
    # citation: str = None
    # # Types
    # ctype: List[NetworkType] = None
    # aspect: Dict[NetworkParamType, ParameterType] = None
    # ftype: Dict[NetworkParamType, FactorType] = None
    # # Collections
    # factors: Dict[NetworkParamType, Factor] = None
    # # Depreciated
    # capacity_scale_level: int = None
    # capex_scale_level: int = None
    # vopex_scale_level: int = None
    # fopex_scale_level: int = None

    # def __post_init__(self):

    #     # *-------------------------- Preprocess data -----------------

    #     # makes dictionary of available transport options between locations
    #     self.transport_dict = self.make_transport_dict()
    #     # makes dictionary of distances between locations
    #     self.distance_dict = self.make_distance_dict()
    #     # same as transport dict, I do not know why I made two, but now I am too scared to change it
    #     self.transport_avail_dict = self.make_transport_avail_dict()

    #     # *-------------------------- Set ctype (NetworkType) -----------------

    #     if self.land_max:
    #         if not self.ctype:
    #             self.ctype = []
    #         self.ctype.append(NetworkType.LAND)

    #     # *-----------------Set aspect (ParameterType) ---------------------------------
    #     # aspects of declared parameters are set to .UNCERTAIN if a MPVar Theta or a tuple of bounds is provided,
    #     # .CERTAIN otherwise
    #     # If empty Theta is provided, the bounds default to (0, 1)

    #     for i in self.aspects():
    #         self.update_network_parameter(parameter=i)

    #     # *-----------------Set ftype (FactorType) ---------------------------------

    #     for i in self.aspects():
    #         self.update_network_factor(parameter=i)

    #     # * ---------------Collect Components (Transport, Locations) -----------------------

    #     self.transports = set()

    #     for i in self.transport_matrix:
    #         for j in i:
    #             for k in j:
    #                 self.transports.add(k)

    #     self.locations = set(self.sources) | set(self.sinks)

    #     self.source_sink_resource_dict = self.make_source_sink_resource_dict()

    #     # * -------------------------- Update Transports ----------------------------------------

    #     if self.capacity_factor:
    #         for location_tuple, transport_and_data in self.capacity_factor.items():
    #             for transport in transport_and_data:
    #                 ctype_intt = [ctype_ for ctype_ in transport.ctype if isinstance(
    #                     ctype_, dict) and list(ctype_)[0] == TransportType.INTERMITTENT]  # get a list of ctypes that are dictionaries and match
    #                 # if already defined, add (Location, Location)
    #                 if ctype_intt:
    #                     ctype_intt[0][TransportType.INTERMITTENT] = ctype_intt[0][TransportType.INTERMITTENT] | {
    #                         location_tuple}
    #                 else:  # else, make a new dictionary for the ctype
    #                     transport.ctype.append(
    #                         {TransportType.INTERMITTENT: {location_tuple}})

    #     for i in self.transport_factors():
    #         self.update_transport_factor(parameter=i)

    #     # * ------------------------- Update Locations----------------------

    #     for i in self.sources:
    #         i.ctype.append(LocationType.SOURCE)
    #     for i in self.sinks:
    #         i.ctype.append(LocationType.SINK)

    #     # *----------------- Depreciation Warnings-----------------------------

    #     if self.capacity_scale_level:
    #         raise ValueError(
    #             f'{self.name}: capacity_scale_level is depreciated. scale levels determined from factor data now')

    #     if self.capex_scale_level:
    #         raise ValueError(
    #             f'{self.name}: capex_scale_level is depreciated. scale levels determined from factor data now')

    #     if self.fopex_scale_level:
    #         raise ValueError(
    #             f'{self.name}: fopex_scale_level is depreciated. scale levels determined from factor data now')

    #     if self.vopex_scale_level:
    #         raise ValueError(
    #             f'{self.name}: vopex_scale_level is depreciated. scale levels determined from factor data now')

    # #  *----------------- Class Methods ---------------------------------------------

    # @classmethod
    # def class_name(cls) -> List[str]:
    #     """Returns class name
    #     """
    #     return cls.__name__

    # # * Network parameters

    # @classmethod
    # def aspects(cls) -> Set[str]:
    #     """All Network parameters
    #     """
    #     return NetworkParamType.all()

    # # * Network classifications

    # @classmethod
    # def ctypes(cls) -> Set[str]:
    #     """All Network classifications
    #     """
    #     return NetworkType.all()

    # # * Network level Transport classifications

    # @classmethod
    # def network_level_transport_classifications(cls) -> Set[str]:
    #     """Set when Network is declared
    #     """
    #     return TransportType.network_level()

    # # * Network level Location classifications

    # @classmethod
    # def network_level_location_classifications(cls) -> Set[str]:
    #     """Set when Network is declared
    #     """
    #     return LocationType.network_level()

    # # * Transport factors

    # @classmethod
    # def transport_factors(cls) -> Set[str]:
    #     """Transport factors updated at Network
    #     """
    #     return TransportParamType.uncertain_factor()

    # # *----------------- Functions-------------------------------------

    # def update_network_parameter(self, parameter: str):
    #     """updates parameter, sets aspect

    #     Args:
    #         parameter (str): parameter to update
    #     """
    #     attr_ = getattr(self, parameter.lower())
    #     if attr_:
    #         aspect_ = getattr(NetworkParamType, parameter)

    #         if not self.aspect:
    #             self.aspect = dict()

    #         if isinstance(attr_, (tuple, Theta)):
    #             self.aspect[aspect_] = ParameterType.UNCERTAIN
    #             theta_ = birth_theta(value=attr_, component=self, aspect=getattr(
    #                 MPVarType, f'{self.class_name()}_{parameter}'.upper()))
    #             setattr(self, parameter.lower(), theta_)
    #         elif isinstance(attr_, Big) or attr_ is True:
    #             self.aspect[aspect_] = ParameterType.BIGM
    #             if attr_ is True:
    #                 setattr(self, parameter.lower(), BigM)
    #         else:
    #             self.aspect[aspect_] = ParameterType.CERTAIN

    # def update_network_factor(self, parameter: str):
    #     """updates factor, sets ftype

    #     Args:
    #         parameter (str): parameter to update
    #     """
    #     attr_ = getattr(self, f'{parameter}_factor'.lower())
    #     if attr_ is not None:
    #         ftype_ = getattr(
    #             FactorType, f'{self.class_name()}_{parameter}'.upper())

    #         if not self.ftype:
    #             self.ftype = set()
    #             self.factors = dict()
    #         self.ftype.add(ftype_)
    #         factor_ = Factor(component=self, data=attr_,
    #                          ftype=ftype_, scales=self.scales)
    #         setattr(self, f'{parameter}_factor'.lower(), factor_)
    #         self.factors[ftype_] = factor_

    # def update_transport_factor(self, parameter: str):
    #     """Updates Transport factor data to Factor and updates ftype and factors
    #     This is similar to Location.update_component_factor
    #     Args:
    #         parameter (str): Transport parameter factor to update
    #     """
    #     factor_name_ = f'{parameter}_factor'.lower()
    #     attr_ = getattr(self, factor_name_)
    #     # if factor is defined at network
    #     if attr_:

    #         for location_tuple, transport_and_data in attr_.items():
    #             for transport, data in transport_and_data.items():
    #                 ftype_ = getattr(
    #                     FactorType, f'{transport.class_name()}_{parameter}'.upper())
    #                 factor_ = Factor(component=transport, data=data, ftype=ftype_,
    #                                  scales=self.scales, location=location_tuple)
    #                 attr_[location_tuple][transport] = factor_
    #                 if not transport.ftype:
    #                     transport.ftype, transport.factors = dict(), dict()
    #                     transport.ftype[ftype_] = {location_tuple}
    #                     transport.factors[ftype_] = dict()
    #                     transport.factors[ftype_][location_tuple] = factor_
    #                 else:
    #                     if ftype_ in transport.ftype:
    #                         transport.ftype[ftype_].add(location_tuple)
    #                         transport.factors[ftype_][location_tuple] = factor_
    #                     else:
    #                         transport.ftype[ftype_] = {location_tuple}
    #                         if ftype_ not in transport.factors:
    #                             transport.factors[ftype_] = dict()
    #                         transport.factors[ftype_][location_tuple] = factor_

    # def make_distance_dict(self) -> dict:
    #     """returns a dictionary of distances from sources to sinks

    #     Returns:
    #         dict: a dictionary of distances from sources to sinks
    #     """
    #     distance_dict = {(self.sources[i], self.sinks[j]):
    #                      self.distance_matrix[i][j] for i, j in
    #                      product(range(len(self.sources)), range(len(self.sinks)))}
    #     return distance_dict

    # def make_transport_dict(self) -> dict:
    #     """returns a dictionary of transportation modes available between sources to sinks

    #     Returns:
    #         dict: a dictionary of transportation modes available between sources to sinks
    #     """
    #     transport_dict = {(self.sources[i], self.sinks[j]):
    #                       set(self.transport_matrix[i][j]) for i, j in
    #                       product(range(len(self.sources)), range(len(self.sinks)))}
    #     return transport_dict

    # def make_transport_avail_dict(self) -> dict:
    #     """returns a dictionary with transportation modes available between sources and sinks

    #     Returns:
    #         dict: a dictionary with transportation modes available between sources and sinks
    #     """
    #     transport_avail_dict = {
    #         i: {j.name for j in self.transport_dict[i]} for i in self.transport_dict}
    #     return transport_avail_dict

    # def make_source_sink_resource_dict(self) -> dict:

    #     source_sink_resource_dict = {
    #         i: None for i in self.transport_dict.keys()}
    #     for i in self.transport_dict:
    #         resources = set()
    #         for j in self.transport_dict[i]:
    #             resources = resources.union({k.name for k in j.resources})
    #         source_sink_resource_dict[i] = resources
    #     return source_sink_resource_dict

    # def __repr__(self):
    #     return self.name

    # def __hash__(self):
    #     return hash(self.name)

    # def __eq__(self, other):
    #     return self.name == other.name
