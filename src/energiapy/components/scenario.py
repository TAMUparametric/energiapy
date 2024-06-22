"""energiapy.Scenario - defined through a Network or a single Location 
"""
# TODO set depreciation warnings
# TODO new way to make subsets
import uuid
from dataclasses import dataclass
from typing import Dict, Union

import numpy
from pandas import DataFrame

from ..model.bounds import CapacityBounds
from ..model.weights import EmissionWeights
from .comptype import LocationType, ProcessType, ResourceType, ScenarioType
from .location import Location
from .network import Network
from .parameters.paratype import ParameterType
from .resource import Resource
from .temporal_scale import TemporalScale


@dataclass
class Scenario:
    """
    Scenario contains the network between location and all the data within.

    Args:
        name (str): name of scenario. Enter None to randomly assign a name.
        scales (temporal_scale): scales of the problem
        network (Union[Network, Location]): network object with the locations, transport linakges, and processes (with resources and materials)
        scheduling_scale_level (int, optional): scale of production and inventory scheduling. Defaults to 0.
        network_scale_level (int, optional): scale for network decisions such as facility location. Defaults to 0.
        demand_scale_level (int, optional): scale for meeting specific demand for resource. Defaults to 0.
        revenue_scale_level (int, optional): scale for revenue from resource. Defaults to 0. 
        cluster_wt (dict): cluster weights as a dictionary. {scale: int}. Defaults to None.
        label (str, optional): Longer descriptive label if required. Defaults to ''
        capacity_bounds (CapacityBounds, optional): bounds on the capacity, useful for multi-period formulations. Defaults to None.
        annualization_factor (float, optional): the annualization factor for Capex. Defaults to 1.
        demand_penalty (Dict[Location, Dict[Resource, float]]): penalty for unmet demand at location for each resource. Defaults to None.
        error (float, optional): error introduced through scenario reduction. Defaults to None.
        rep_days_dict (dict, optional): dictionary of representative days. Defaults to None.
        emission_weights (EmissionWeights): dataclass with weights for different emission objectives. Defaults to None. 
    Example:
        The Scenario can be built over a single location. The network here is specified as a single Location. Considering scales (TemporalScale object for a year, [1, 365, 24]), scheduling, expenditure, and demand are met at an hourly level, and network at an annual level.

        >>> Current = Scenario(name= 'current', network= Goa, scales= scales, scheduling_scale_level= 2, network_scale_level= 0, demand_scale_level= 2, label= 'Current Scenario')

        A multilocation Scenario needs a Network to be provided. Here, expenditure (on resource purchase) is determined at a daily scale. price_factor in the Location object needs to be commensurate in scale.

        >>> Future = Scenario(name= 'Future', network= System, scales= scales, scheduling_scale_level= 2, network_scale_level= 0, demand_scale_level= 2, label= 'Future Scenario' )
    """
    name: str
    scales: TemporalScale
    network: Union[Network, Location] = None
    cluster_wt: dict = None
    label: str = ''
    capacity_bounds: CapacityBounds = None
    annualization_factor: float = 1
    demand_penalty: Dict[Location, Dict[Resource, float]] = None
    error: float = None
    rep_dict: dict = None
    emission_weights: EmissionWeights = None
    ctype: ScenarioType = None
    # Depriciated
    purchase_scale_level: int = None
    expenditure_scale_level: int = None
    scheduling_scale_level: int = None
    availability_scale_level: int = None
    network_scale_level: int = None
    demand_scale_level: int = None
    capacity_scale_level: int = None
    demand: dict = None

    def __post_init__(self):
        """
        Determines a bunch of handy sets

        Args:
            transport_set (set): Set of transport options.
            source_locations (set): Set of source locations.
            sink_locations (set): Set of sink locations.
            transport_dict (dict): A dictionary of trasportation modes available between sources to sinks
            transport_avail_dict (dict): A dictionary of available trasportation modes available between sources to sinks.
            transport_max (dict): A dictionary of the maximum amount of each resource that can be transported between sources and sinks.
            transport_loss (dict): A dictionary of the transport losses for each resource that can be transported between sources and sinks.
            transport_cost (dict): A dictionary of the transport cost for each resource that can be transported between sources and sinks.
            transport_cost (dict): A dictionary of the transport emissions for each resource that can be transported between sources and sinks.
            distance_dict (dict): A dictionary of distances between sources and sinks.
            demand_factor_scale_level (int, optional): scale level for demand variance (resource). Defaults to 0
            price_factor_scale_level (int, optional): scale level for purchase cost variance(resource). Defaults to 0
            capacity_factor_scale_level (int, optional): scale level for capacity variance(process). Defaults to 0
            expenditure_factor_scale_level (int, optional): scale level for technology cost variance (process). Defaults to 0
            availability_factor_scale_level (int, optional): scale level for availability varriance (resource). Defaults to 0
            revenue_factor_scale_level (int, optional): scale level for revenue varriance (resource). Defaults to 0
            processes (set): Set of all Process objects.
            resources (set): Set of all Resource objects.
            materials (set): Set of all Material objects.
            conversion (dict): A dictionary with all conversion values for each Process.
            conversion_discharge (dict): A dictionary with all discharge conversions for Process of storage (ProcessMode.STORAGE) type.
            cap_max (dict): A dictionary with maximum production capacity per timeperiod in the network scale for each Process at each Location.
            cap_min (dict): A dictionary with minimum production capacity per timeperiod in the network scale for each Process at each Location.
            cons_max (dict): A dictionary with maximum consumption per timeperiod in the scheduling scale for each Resource at each Location.
            store_max (dict): A dictionary with maximum storage per timeperiod in the scheduling scale for each Resource at each Location.
            store_min (dict): A dictionary with minimum storage per timeperiod in the scheduling scale for each Resource at each Location.
            capacity_factor (dict): A dictionary with Location-wise capacity factors for varying Process objects.
            price_factor (dict): A dictionary with Location-wise cost factors for varying purchase costs of Resource objects.
            demand_factor (dict): A dictionary with Location-wise demand factors for varying demands of Resource objects.
            location_resource_dict (dict): A dictionary with Location-wise availability of Resource objects.
            location_process_dict (dict): A dictionary with Location-wise availability of Process objects.
            location_material_dict (dict): A dictionary with Location-wise availability of Material objects.
            price_dict (dict): A dictionary with Location-wise purchase price of Resource objects
            revenue_dict (dict): A dictionary with Location-wise revenue from selling resource objects
            capex_dict (dict): A dictionary with capital expenditure data for each Process.
            fopex_dict (dict): A dictionary with fixed operational expenditure data for each Process.
            vopex_dict (dict): A dictionary with variable operational expenditure data for each Process.
            incidental_dict (dict): A dictionary with incidental expenditure data for each Process.
            land_dict (dict): A dictionary with land use data for each Process.
            material_gwp_dict (dict): A dictionary with global warming potential values for each Material object.
            resource_gwp_dict (dict): A dictionary with global warming potential values for each Resource object.
            process_gwp_dict (dict): A dictionary with global warming potential values for each Process object.
            fail_factor (dict): A dictionary with fail factors for each Process object.
            process_resource_dict (dict): A dictionary with Resource required for each Process.
            process_material_dict (dict): A dictionary with Material required for each Process
            mode_dict (dict): A dictionary with the multiple modes of each Process with ProcessMode.MULTI
            cost_df (DataFrame): handy dataframe with cost parameters
        """

        self.design_scale = self.scales.design_scale
        self.scheduling_scale = self.scales.scheduling_scale

        if isinstance(self.network, Location):
            self.ctype = ScenarioType.SINGLE_LOCATION
            self.locations = {self.network}

            # self.transport_set = None
            # self.source_locations = None
            # self.sink_locations = None
            # self.transport_dict = None
            # self.transport_avail_dict = None
            # self.trans_max = None
            # self.trans_loss = None
            # self.trans_capex = None
            # self.trans_fopex = None
            # self.trans_vopex = None
            # self.trans_emission = None
            # self.distance_dict = None
            # self.transport_capacity_factor = None
            # self.transport_capex_factor = None
            # self.transport_vopex_factor = None
            # self.transport_fopex_factor = None
            # self.transport_capacity_scale_level = None
            # self.transport_capex_scale_level = None
            # self.transport_vopex_scale_level = None
            # self.transport_fopex_scale_level = None
            # self.source_sink_resource_dict = None
        else:
            self.ctype = ScenarioType.MULTI_LOCATION
            self.transport_set = set().union(*self.network.transport_dict.values())
            self.source_locations = self.network.source_locations
            self.sink_locations = self.network.sink_locations
            self.transport_dict = self.network.transport_dict
            self.transport_avail_dict = self.network.transport_avail_dict
            self.locations = set(
                self.source_locations + self.sink_locations)
            # self.trans_max = {j.name: j.trans_max for j in self.transport_set}
            # self.trans_min = {j.name: j.trans_min for j in self.transport_set}
            # self.trans_loss = {
            #     j.name: j.trans_loss for j in self.transport_set}
            # self.trans_capex = {
            #     j.name: j.capex for j in self.transport_set}
            # self.trans_vopex = {
            #     j.name: j.vopex for j in self.transport_set}
            # self.trans_fopex = {
            #     j.name: j.fopex for j in self.transport_set}
            # self.trans_emission = {
            #     j.name: j.emission for j in self.transport_set}
            # self.distance_dict = self.network.distance_dict
            # # self.transport_resource_dict = {i: None for i in self.transport_dict.keys()}
            # self.location_transport_resource_dict = {i: {k.name: {
            #     l.name for l in k.resources} for k in j} for i, j in self.transport_dict.items()}
            # self.resource_transport_dict = {}
            # for key, value in {i.name: i.resources for i in self.transport_set}.items():
            #     for item in value:
            #         if item in self.resource_transport_dict:
            #             self.resource_transport_dict[item].append(key)
            #         else:
            #             self.resource_transport_dict[item] = [key]
            # self.resource_transport_dict = {
            #     i.name: j for i, j in self.resource_transport_dict.items()}
            # self.transport_resource_dict = {
            #     i.name: {j.name for j in i.resources} for i in self.transport_set}
            # # for i,j in self.transport_dict.items():
            # #     set_ = set()
            # #     for k in j:
            # #         set_ = set_.union(k.resources)
            # #     self.transport_resource_dict[i] = {i.name for i in set_}
            # self.transport_capacity_factor = self.network.transport_capacity_factor
            # self.transport_capex_factor = self.network.transport_capex_factor
            # self.transport_vopex_factor = self.network.transport_vopex_factor
            # self.transport_fopex_factor = self.network.transport_fopex_factor
            # self.transport_capacity_scale_level = self.network.transport_capacity_scale_level
            # self.transport_capex_scale_level = self.network.transport_capex_scale_level
            # self.transport_vopex_scale_level = self.network.transport_vopex_scale_level
            # self.transport_fopex_scale_level = self.network.transport_fopex_scale_level
            # self.source_sink_resource_dict = self.network.source_sink_resource_dict

        self.processes = set().union(
            *[i.processes for i in self.locations if i.processes is not None])
        self.resources = set().union(
            *[i.resources for i in self.locations if i.resources is not None])
        self.materials = set().union(
            *[i.materials for i in self.locations if i.materials is not None])
        self.demand = {i: i.demand for i in self.locations}
        self.conversion = {i.name: {j.name: i.conversion[j] if j in i.conversion.keys(
        ) else 0 for j in self.resources} for i in self.processes if i.conversion is not None}

        self.process_resources = {
            i: i.resource_req for i in self.processes}

        self.process_materials = {
            i: {j: i.material_cons[j] if j in i.material_cons.keys() else 0 for j in self.materials} for i in self.processes}

        self.location_resources = {i: {j for j in i.resources}
                                   for i in self.locations}

        self.location_processes = {i: {j for j in i.processes}
                                   for i in self.locations}

        self.location_materials = {i: {j for j in i.materials}
                                   for i in self.locations}

        for i in ['cap_max', 'cap_min', 'purchase_price', 'sell_price', 'cons_max', 'store_max', 'store_min', 'storage_cost', 'capacity_factor', 'purchase_price_factor', 'demand_factor', 'capex_factor',
                  'fopex_factor', 'vopex_factor', 'incidental_factor', 'availability_factor', 'sell_price_factor']:
            self.loc_comp_attr_dict(attr=i)

        for i in ['store', 'produce', 'implicit', 'discharge', 'sell', 'consume', 'purchase', 'demand']:
            setattr(self, f'location_resources_{i}', {j: getattr(
                j, f'resources_{i}') for j in self.locations})
            setattr(self, f'resources_{i}', set().union(
                *[getattr(j, f'resources_{i}') for j in self.locations]))

        for i in ['capex', 'fopex', 'vopex', 'incidental', 'land']:
            self.create_attr_dict(i, self.processes)

        # df_capex = DataFrame.from_dict(
        #     self.capex_dict, orient='index', columns=['capex'])
        # df_vopex = DataFrame.from_dict(
        #     self.vopex_dict, orient='index', columns=['vopex'])
        # df_fopex = DataFrame.from_dict(
        #     self.fopex_dict, orient='index', columns=['fopex'])

        # self.cost_df = df_capex.merge(df_vopex, left_index=True, right_index=True, how='inner').merge(
        #     df_fopex, left_index=True, right_index=True, how='inner')

        # * ---------------- Collect Emission Data ------------------------------------------
        # Get emission data from components
        for i in ['resources', 'materials', 'processes']:
            setattr(self, f'{i}_emissions', {
                    j: j.emissions for j in getattr(self, i)})

        # self.material_gwp_dict = {
        #     i.name: {j.name: j.gwp for j in self.materials} for i in self.locations}
        # self.material_odp_dict = {
        #     i.name: {j.name: j.odp for j in self.materials} for i in self.locations}
        # self.material_acid_dict = {
        #     i.name: {j.name: j.acid for j in self.materials} for i in self.locations}
        # self.material_eutt_dict = {
        #     i.name: {j.name: j.eutt for j in self.materials} for i in self.locations}
        # self.material_eutf_dict = {
        #     i.name: {j.name: j.eutf for j in self.materials} for i in self.locations}
        # self.material_eutm_dict = {
        #     i.name: {j.name: j.eutm for j in self.materials} for i in self.locations}
        # self.resource_gwp_dict = {
        #     i.name: {j.name: j.gwp for j in self.resources} for i in self.locations}
        # self.resource_odp_dict = {
        #     i.name: {j.name: j.odp for j in self.resources} for i in self.locations}
        # self.resource_acid_dict = {
        #     i.name: {j.name: j.acid for j in self.resources} for i in self.locations}
        # self.resource_eutt_dict = {
        #     i.name: {j.name: j.eutt for j in self.resources} for i in self.locations}
        # self.resource_eutf_dict = {
        #     i.name: {j.name: j.eutf for j in self.resources} for i in self.locations}
        # self.resource_eutm_dict = {
        #     i.name: {j.name: j.eutm for j in self.resources} for i in self.locations}
        # self.process_gwp_dict = {
        #     i.name: {j.name: j.gwp for j in self.processes} for i in self.locations}
        # self.process_odp_dict = {
        #     i.name: {j.name: j.odp for j in self.processes} for i in self.locations}
        # self.process_acid_dict = {
        #     i.name: {j.name: j.acid for j in self.processes} for i in self.locations}
        # self.process_eutt_dict = {
        #     i.name: {j.name: j.eutt for j in self.processes} for i in self.locations}
        # self.process_eutf_dict = {
        #     i.name: {j.name: j.eutf for j in self.processes} for i in self.locations}
        # self.process_eutm_dict = {
        #     i.name: {j.name: j.eutm for j in self.processes} for i in self.locations}

        self.fail_factor = {i.name: i.fail_factor for i in self.locations}

        self.process_material_mode_material_dict = {i.name: {j: {l.name: m for l, m in k.items(
        )} for j, k in i.material_cons.items()} for i in self.processes if ProcessType.MULTI_MATMODE in i.ctype}
        multiconversion_dict = dict()
        for i in self.processes:
            if ProcessType.MULTI_PRODMODE in i.ctype:
                multiconversion_dict[i.name] = {
                    j: None for j in i.conversion.keys()}
                for k in list(multiconversion_dict[i.name].keys()):
                    multiconversion_dict[i.name][k] = {j.name: i.conversion[k][j] if j in i.conversion[k].keys() else 0
                                                       for j in self.resources}
            else:
                multiconversion_dict[i.name] = {0: None}
                multiconversion_dict[i.name][0] = {j.name: i.conversion[j] if j in i.conversion.keys() else 0 for j in
                                                   self.resources}

        self.multiconversion = multiconversion_dict

        self.mode_dict = {i.name: list(
            self.multiconversion[i.name].keys()) for i in self.processes if ProcessType.MULTI_PRODMODE in i.ctype}
        # self.mode_dict = {i: [(k,) for k in j]for i,j in self.mode_dict.items()}

        # self.modes_dict = {i: i.modes_dict for i in self.locations}

        if self.demand_penalty is not None:
            self.demand_penalty = {i.name: {j.name: self.demand_penalty[i][j] for j in self.demand_penalty[i].keys(
            )} for i in self.demand_penalty.keys()}

        # self.rate_max_dict = {i.name: i.rate_max for i in self.processes}

        # self.mode_ramp_dict = {i.name: i.mode_ramp for i in self.processes}

        self.process_material_modes = []
        for i in self.processes:
            if i.material_cons is not None:

                process_material_modes = process_material_modes + \
                    [(i.name, j) for j in list(i.material_cons.keys())]
                if i.material_cons != {}:
                    self.process_material_modes = process_material_modes

                    self.process_material_modes_dict = {
                        i.name: i.material_modes for i in self.processes}

        self.component_sets = {
            'resources': [i.name for i in self.resources],
            'processes': [i.name for i in self.processes],
            'materials': [i.name for i in self.materials],
            'locations': [i.name for i in self.locations],
            'transports': [i.name for i in self.transport_set]
        }

        self.resource_subsets = dict()

        for i in ['store', 'produce', 'implicit', 'discharge', 'sell', 'consume', 'purchase', 'demand']:
            self.resource_subsets[f'resources_{i}'] = [
                i.name for i in getattr(self, f'resources_{i}')]

        for j in ['demand', 'purchase', 'sell', 'consume']:
            # TODO - location specific factor and localization sets
            self.resource_subsets[f'resources_varying_{j}'] = [i.name for i in getattr(
                self, f'resources_{j}') if i.ptype[getattr(ResourceType, j.upper())] == ParameterType.FACTOR]

            self.resource_subsets[f'resources_certain_{j}'] = [i.name for i in getattr(
                self, f'resources_{j}') if i.ptype[getattr(ResourceType, j.upper())] == ParameterType.CERTAIN]

            self.resource_subsets[f'resources_uncertain_{j}'] = [i.name for i in getattr(
                self, f'resources_{j}') if i.ptype[getattr(ResourceType, j.upper())] == ParameterType.UNCERTAIN]

        self.resource_subsets['resources_transport'] = [
            i.name for i in self.resources if ResourceType.TRANSPORT in i.ctype]

        self.process_subsets = dict()

        for j in ['capacity', 'capex', 'fopex', 'vopex', 'incidental']:
            # TODO - location specific factor and localization sets

            self.process_subsets[f'processes_varing_{j}'] = [i.name for i in self.processes if getattr(ProcessType, j.upper(
            )) in i.ptype.keys() if i.ptype[getattr(ProcessType, j.upper())] == ParameterType.FACTOR]

            self.process_subsets[f'processes_certain_{j}'] = [i.name for i in self.processes if getattr(ProcessType, j.upper(
            )) in i.ptype.keys() if i.ptype[getattr(ProcessType, j.upper())] == ParameterType.CERTAIN]

            self.process_subsets[f'processes_uncertain_{j}'] = [i.name for i in self.processes if getattr(ProcessType, j.upper(
            )) in i.ptype.keys() if i.ptype[getattr(ProcessType, j.upper())] == ParameterType.UNCERTAIN]

        for j in ['single_prodmode', 'multi_prodmode', 'no_matmode', 'multi_matmode', 'single_matmode', 'storage', 'storage_req', 'linear_capex', 'pwl_capex', 'land']:
            self.process_subsets[f'processes_{j}'] = [
                i.name for i in self.processes if getattr(ProcessType, j.upper()) in i.ctype]

        self.process_subsets['processes_failure'] = [
            i.name for i in self.processes if i.p_fail is not None]

        self.location_subsets = dict()

        self.location_subsets['sources'] = [
            i.name for i in self.locations if LocationType.SOURCE in i.ctype]
        self.location_subsets['sinks'] = [
            i.name for i in self.locations if LocationType.SINK in i.ctype]
        self.location_subsets['locations_land_cost'] = [
            i.name for i in self.locations if LocationType.LAND_COST in i.ctype]

        # self.location_subsets['locations_varying_land_cost'] = [i.name for i in self.locations if LocationType.LAND_COST in i.ptype.keys(
        # ) if i.ptype[LocationType.LAND_COST] == ParameterType.FACTOR]
        # self.location_subsets['locations_certain_land_cost'] = [
        #     i.name for i in self.locations if LocationType.LAND_COST in i.ptype.keys() if i.ptype[LocationType.LAND_COST] == ParameterType.CERTAIN]
        # self.location_subsets['locations_uncertain_land_cost'] = [
        #     i.name for i in self.locations if LocationType.LAND_COST in i.ptype.keys() if i.ptype[LocationType.LAND_COST] == ParameterType.UNCERTAIN]

        # self.location_land_cost_factor = {
        #     i: i.land_cost_factor for i in self.location_subsets['locations_varying_land_cost']}

        # self.land_cost_dict = {
        #     i.name: i.land_cost for i in self.locations if LocationType.LAND_COST in i.ctype}

        # self.credit_dict = {i.name: {j.name: i.credit[j] for j in i.credit.keys(
        # )} for i in self.locations if i.credit is not None}

        # self.set_dict = {x: sorted(set_dict[x]) for x in set_dict.keys()}

        # if self.ctype == ScenarioType.MULTI_LOCATION:

        #     transport_set_dict = {
        #         'transports_certain_capacity': [i.name for i in self.transport_set if VaryingTransport.CERTAIN_CAPACITY in i.varying],
        #         'transports_certain_capex': [i.name for i in self.transport_set if VaryingTransport.CERTAIN_CAPEX in i.varying],
        #         'transports_certain_vopex': [i.name for i in self.transport_set if VaryingTransport.CERTAIN_VOPEX in i.varying],
        #         'transports_certain_fopex': [i.name for i in self.transport_set if VaryingTransport.CERTAIN_FOPEX in i.varying],

        #         'transports_uncertain_capacity': [i.name for i in self.transport_set if VaryingTransport.UNCERTAIN_CAPACITY in i.varying],
        #         'transports_uncertain_capex': [i.name for i in self.transport_set if VaryingTransport.UNCERTAIN_CAPEX in i.varying],
        #         'transports_uncertain_vopex': [i.name for i in self.transport_set if VaryingTransport.UNCERTAIN_VOPEX in i.varying],
        #         'transports_uncertain_fopex': [i.name for i in self.transport_set if VaryingTransport.UNCERTAIN_FOPEX in i.varying],

        #         'transports_varying_capacity': [i.name for i in self.transport_set if VaryingTransport.DETERMINISTIC_CAPACITY in i.varying],
        #         'transports_varying_capex': [i.name for i in self.transport_set if VaryingTransport.DETERMINISTIC_CAPEX in i.varying],
        #         'transports_varying_vopex': [i.name for i in self.transport_set if VaryingTransport.DETERMINISTIC_VOPEX in i.varying],
        #         'transports_varying_fopex': [i.name for i in self.transport_set if VaryingTransport.DETERMINISTIC_FOPEX in i.varying],
        #     }
        #     self.set_dict = {}
        #     self.set_dict = {**self.set_dict, **transport_set_dict}

        # self.mode_sets = dict()

        # self.mode_sets['processes_material_modes'] = self.process_material_modes
        # self.mode_sets['material_modes'] = [element for dictionary in list(
        #     i.material_modes for i in self.processes) for element in dictionary]
        # self.mode_sets['process_modes'] = [(j[0], i) for j in [(
        #     i.name, i.modes) for i in self.processes if ProcessType.MULTI_PRODMODE in i.ctype] for i in j[1]]

        # self.varying_bounds_dict = {
        #     'demand': {i.name: i.varying_bounds for i in self.resources if VaryingResource.UNCERTAIN_DEMAND in i.varying},
        #     'availability': {i.name: i.varying_bounds for i in self.resources if VaryingResource.UNCERTAIN_AVAILABILITY in i.varying},
        #     'capacity': {i.name: i.varying_bounds for i in self.processes if VaryingProcess.UNCERTAIN_CAPACITY in i.varying}
        # }

        if self.name is None:
            self.name = f'{self.__class__.__name__}_{uuid.uuid4().hex}'

    def loc_comp_attr_dict(self, attr: str):
        """creates a dict of type {loc: {comp: attribute_dict}}
        Args:
            attr (str): attribute
        """
        check_set = {getattr(i, attr) if isinstance(
            getattr(i, attr), dict) is False else 1 for i in getattr(self, 'locations')}
        if list(set(check_set))[0] is not None:
            setattr(self, attr, {i: getattr(
                i, attr) for i in getattr(self, 'locations')})
        else:
            setattr(self, f'{attr}', None)

    def loc_comp_dict(self, attr: str, attr_tag: str):
        """creates dict of the type {loc: {comp subset}}
        Args:
            attr (str): location attribute to select
            attr_tag (str): what should the dict be tagged as
        """
        setattr(self, f'location_{attr_tag}_dict',
                {getattr(i, 'name'): {getattr(j, 'name') for j in getattr(i, attr)} for i in getattr(self, 'locations')})

    def create_attr_dict(self, attr: str, component_set: set):
        """Checks whether atleast one component in set has attribute not None
        If True, create a dict to save said attribute
        And, sets consider_attr to True. Else False
        Args:
            attr (str): component attribute
            component_set (set): self explanatory
        """
        if list({getattr(i, attr) for i in component_set})[0] is not None:
            setattr(self, f'consider_{attr}', True)
            setattr(self, f'{attr}_dict',
                    {i.name: getattr(i, attr) for i in component_set})
        else:
            setattr(self, f'consider_{attr}', False)

    def make_conversion_df(self) -> DataFrame:
        """makes a DataFrame of the conversion values

        Returns:
            DataFrame: DataFrame of conversion values 
        """
        return DataFrame.from_dict(self.conversion).transpose()

    def make_material_df(self) -> DataFrame:
        """makes a DataFrame of material consumption

        Returns:
            DataFrame: DataFrame of material consumption 
        """
        return DataFrame.from_dict(self.process_material_dict).transpose()

    def matrix_form(self):
        """returns matrices for the scenario.

        Returns:
            tuple: A, b, c, H, CRa, CRb, F
        """
        demand = self.demand
        if isinstance(demand, dict):
            if isinstance(list(demand.keys())[0], Location):
                try:
                    self.demand = {i.name: {
                        j.name: demand[i][j] for j in demand[i].keys()} for i in demand.keys()}
                except:
                    pass
        if len(self.locations) > 1:
            print("can only do this for a single location scenario")
        else:
            location = list(self.locations)[0].name

            # find number of different variables
            # Inv - inventory
            # S - Sell/Discharge
            # C - Resource cost
            # A - Availability
            # P - Production

            n_Inv = len(self.set_dict['resources_store'])

            n_Sf = len(self.set_dict['resources_certain_demand'])
            n_S = len(self.set_dict['resources_uncertain_demand'])
            n_Snd = len([i for i in self.set_dict['resources_sell']
                         if i not in self.set_dict['resources_demand']])
            n_Af = len(self.set_dict['resources_certain_availability'])
            n_A = len(self.set_dict['resources_uncertain_availability'])

            n_Pf = len(self.set_dict['processes_certain_capacity'])
            n_P = len(self.set_dict['processes_uncertain_capacity'])

            n_Cf = len(self.set_dict['resources_certain_price'])
            n_C = len(self.set_dict['resources_uncertain_price'])

            n_I = len(self.set_dict['resources_implicit'])

            n_bal = n_P + n_Pf  # number of production processes for resource balance constraint

            # used to balance implicitly made resources
            n_bal2 = n_Inv + n_Sf + n_S + n_Snd + n_Af + n_A

            n_vars_fix = n_Inv + n_Sf + n_Snd + n_Af + \
                n_Pf  # total number of fixed variables

            n_vars_theta = n_S + n_A + n_P  # total number of theta variables

            n_vars = n_vars_fix + n_vars_theta  # total number of variables

            print('The problem has the following variables:')
            print(f"Resource inventory level (Inv) x {n_Inv}")
            print(f"Exact resource discharge (Sf) x {n_Sf}")
            print(f"Uncertain resource discharge (S) x {n_S}")
            print(f"Resources discharge no demand (Snd) x {n_Snd}")
            print(f"Exact resource availability (Af) x {n_Af}")
            print(f"Uncertain resource availability (A) x {n_A}")
            print(f"Implicit resource (I) x {n_I}")
            print(f"Exact resource price (Cf) x {n_Cf}")
            print(f"Uncertain resource price (C) x {n_C}")
            print(f"Exact process production (Pf) x {n_Pf}")
            print(f"Uncertain process production (P) x {n_P}")
            print(
                f" For a total of {n_vars} ({n_vars_fix} fixed, and {n_vars_theta} uncertain)")

            # *--------------------------------A--------------------------------------
            A_bal = numpy.diag(
                [*[1] * n_Inv, *[-1] * n_Sf, *[-1] * n_S, *[-1]*n_Snd, *[1] * n_Af, *[1] * n_A])

            if n_I > 0:  # if implict variables present, add 0 stacks to matrix

                A_bal = numpy.vstack((A_bal, n_I*[[0]*(n_bal2)]))

            conversion_list = self.set_dict['resources_store'] + self.set_dict['resources_certain_demand'] + \
                self.set_dict['resources_uncertain_demand'] + \
                [i for i in self.set_dict['resources_sell'] if i not in self.set_dict['resources_demand']] + \
                self.set_dict['resources_certain_availability'] + \
                self.set_dict['resources_uncertain_availability'] + \
                self.set_dict['resources_implicit']

            column_list_vars = [*['Inv_' + i for i in self.set_dict['resources_store']] +
                                ['Sf_' + i for i in self.set_dict['resources_certain_demand']] +
                                ['S_' + i for i in self.set_dict['resources_uncertain_demand']] +
                                ['Snd_' + i for i in [i for i in self.set_dict['resources_sell'] if i not in self.set_dict['resources_demand']]] +
                                ['Af_' + i for i in self.set_dict['resources_certain_availability']] +
                                ['A_' + i for i in self.set_dict['resources_uncertain_availability']] +
                                ['Pf_' + i for i in self.set_dict['processes_certain_capacity']] +
                                ['P_' + i for i in self.set_dict['processes_uncertain_capacity']]]

            A_conv = numpy.array([[self.conversion[i][j] for j in conversion_list] for i in
                                  sorted(self.conversion.keys())]).transpose()

            A_diag = numpy.diag(
                [*[1]*n_Inv, *[-1]*n_Sf, *[-1]*n_S, *[-1]*n_Snd,  *[1]*n_Af, *[1] * n_A, *[1]*n_Pf, *[1]*n_P])

            row_diag = [*['Inv_' + i + '(<)' for i in self.set_dict['resources_store']] +
                        ['Sf_' + i + '(>)' for i in self.set_dict['resources_certain_demand']] +
                        ['S_' + i + '(>)' for i in self.set_dict['resources_uncertain_demand']] +
                        ['Snd_' + i + '(>)' for i in [i for i in self.set_dict['resources_sell'] if i not in self.set_dict['resources_demand']]] +
                        ['Af_' + i + '(<)' for i in self.set_dict['resources_certain_availability']] +
                        ['A_' + i + '(<)' for i in self.set_dict['resources_uncertain_availability']] +
                        ['Pf_' + i + '(<)' for i in self.set_dict['processes_certain_capacity']] +
                        ['P_' + i + '(<)' for i in self.set_dict['processes_uncertain_capacity']]]

            row_NN = [*['NN_Inv_' + i + '(>)' for i in self.set_dict['resources_store']] +
                      ['NN_Sf_' + i + '(>)' for i in self.set_dict['resources_certain_demand']] +
                      ['NN_S_' + i + '(>)' for i in self.set_dict['resources_uncertain_demand']] +
                      ['NN_Snd_' + i + '(>)' for i in [i for i in self.set_dict['resources_sell'] if i not in self.set_dict['resources_demand']]] +
                      ['NN_Af_' + i + '(>)' for i in self.set_dict['resources_certain_availability']] +
                      ['NN_A_' + i + '(>)' for i in self.set_dict['resources_uncertain_availability']] +
                      ['NN_Pf_' + i + '(>)' for i in self.set_dict['processes_certain_capacity']] +
                      ['NN_P_' + i + '(>)' for i in self.set_dict['processes_uncertain_capacity']]]

            row_bal = ['MB_' + i + '(=)' for i in self.set_dict['resources_store']
                       + self.set_dict['resources_certain_demand']
                       + self.set_dict['resources_uncertain_demand']
                       + [i for i in self.set_dict['resources_sell']
                          if i not in self.set_dict['resources_demand']]
                       + self.set_dict['resources_certain_availability']
                       + self.set_dict['resources_uncertain_availability']
                       + self.set_dict['resources_implicit']]

            row_list = row_bal + row_diag + row_NN

            # print(row_list)
            A_nn = numpy.eye(n_vars)

            A = numpy.block(
                [[numpy.block([A_bal, A_conv])], [A_diag], [-A_nn]])

            self.A_df = DataFrame(A, columns=column_list_vars)
            self.A_df.index = row_list

            # *-----------------------b------------------------------------------------

            # prod max has 0 because the default mode is 0
            b_bal = numpy.zeros((n_bal2 + n_I, 1))
            b_Inv = numpy.array([[self.store_max[location][i]]
                                for i in self.set_dict['resources_store']])  # fixed storage bound
            b_Sf = numpy.array([[-self.demand[location][i]]
                                for i in self.set_dict['resources_certain_demand']])  # fixed demand bound
            b_S = numpy.array([[0]
                               for i in self.set_dict['resources_uncertain_demand']])  # uncertain demand
            b_Snd = numpy.array([[0]
                                 for i in [i for i in self.set_dict['resources_sell'] if i not in self.set_dict['resources_demand']]])  # sell but no demand
            # b_S = numpy.array([[-self.demand[location][i]]
            #    for i in self.set_dict['resources_uncertain_demand']])  # uncertain demand
            b_Af = numpy.array([[self.cons_max[location][i]]
                                for i in self.set_dict['resources_certain_availability']])  # fixed availability bound
            b_A = numpy.array([[self.cons_max[location][i]]
                               for i in self.set_dict['resources_uncertain_availability']])  # uncertain availability

            b_Pf = numpy.array([[self.cap_max[location][i][0]]
                                for i in self.set_dict['processes_certain_capacity']])  # fixed production bound
            # b_P = numpy.array([[self.cap_max[location][i][0]]
            #                    for i in self.set_dict['processes_uncertain_capacity']])  # uncertain production

            # uncertain production
            b_P = numpy.array(
                [[0] for i in self.set_dict['processes_uncertain_capacity']])

            b_nn = numpy.zeros((n_vars, 1))  # non zero constraints

            b_list = [b_bal, b_Inv, b_Sf, b_S,
                      b_Snd, b_Af, b_A, b_Pf, b_P, b_nn]

            b = numpy.block([[i]
                            for i in b_list if len(i) > 0])  # make b matrix
            self.b_df = DataFrame(b, columns=['rhs'])
            self.b_df.index = row_list

            # *------------------------------- F --------------------------------------

            F = numpy.zeros((len(b), n_vars_theta))  # make F matrix

            n_bal3 = n_bal2 + n_I
            iter_ = 0
            for i in range(n_S):
                n = n_Inv + n_Sf
                F[n_bal3 + n +
                    iter_][i] = -self.demand[location][self.set_dict['resources_uncertain_demand'][i]]
                iter_ += 1

            iter_ = 0
            for i in range(n_A):
                n = n_Inv + n_Sf + n_S + n_Snd + n_Af
                F[n_bal3 + n + iter_][n_S + i] = self.cons_max[location][
                    self.set_dict['resources_uncertain_availability'][i]]
                iter_ += 1

            iter_ = 0
            for i in range(n_P):
                n = n_Inv + n_Sf + n_S + n_Snd + n_Af + n_A + n_Pf
                F[n_bal3 + n + iter_][n_S + n_A +
                                      i] = self.cap_max[location][self.set_dict['processes_uncertain_capacity'][i]][0]
                # defaults to 0 as mode, using P_m instead of P
                iter_ += 1

            column_list_theta = [*['Th_' + i for i in self.set_dict['resources_uncertain_demand']] + ['Th_' + i for i in
                                                                                                      self.set_dict['resources_uncertain_availability']] + ['Th_' + i for i in self.set_dict['processes_uncertain_capacity']]]
            self.F_df = DataFrame(F, columns=column_list_theta)
            self.F_df.index = row_list

            # *--------------------------------------c--------------------------------------
            c_Inv = numpy.zeros((n_Inv, 1))
            c_Sf = numpy.zeros((n_Sf, 1))
            c_S = numpy.zeros((n_S, 1))
            c_Snd = numpy.zeros((n_Snd, 1))

            # c_Af = numpy.zeros((n_Af, 1))
            # c_A = numpy.zeros((n_A, 1))

            c_Cf = numpy.array([[self.price_dict[list(self.locations)[0].name][i]]
                               for i in self.set_dict['resources_certain_price']])
            c_C = numpy.array([[self.price_dict[list(self.locations)[0].name][i]]
                              for i in self.set_dict['resources_uncertain_price']])

            c_Pf = numpy.array([[self.vopex_dict[i]]
                                for i in self.set_dict['processes_certain_capacity']])
            c_P = numpy.array([[self.vopex_dict[i]]
                               for i in self.set_dict['processes_uncertain_capacity']])
            c_list = [c_Inv, c_Sf,  c_S, c_Snd, c_Cf, c_C, c_Pf, c_P]
            c = numpy.block([[i] for i in c_list if len(i) > 0])

            self.c_df = DataFrame(c)
            self.c_df.index = column_list_vars
            # *-------------------------------------H----------------------------------------

            H = numpy.zeros((A.shape[1], F.shape[1]))

            self.H_df = DataFrame(H, columns=column_list_theta)
            self.H_df.index = column_list_vars
            # *----------------------------------critical regions---------------------------

            CRa = numpy.vstack(
                (numpy.eye(n_vars_theta), -numpy.eye(n_vars_theta)))

            self.CRa_df = DataFrame(CRa, columns=column_list_theta)
            self.CRa_df.index = [
                'UB_' + i for i in column_list_theta] + ['LB_' + i for i in column_list_theta]

            CRb_UB = [self.varying_bounds_dict['demand'][i][1] for i in self.set_dict['resources_uncertain_demand']] + [self.varying_bounds_dict['capacity'][i][1]
                                                                                                                        for i in self.set_dict['processes_uncertain_capacity']] + [self.varying_bounds_dict['availability'][i][1] for i in self.set_dict['resources_uncertain_availability']]
            CRb_LB = [-self.varying_bounds_dict['demand'][i][0] for i in self.set_dict['resources_uncertain_demand']] + [self.varying_bounds_dict['capacity'][i][0]
                                                                                                                         for i in self.set_dict['processes_uncertain_capacity']] + [self.varying_bounds_dict['availability'][i][0] for i in self.set_dict['resources_uncertain_availability']]

            CRb = numpy.array([*CRb_UB, *CRb_LB]).reshape(n_vars_theta * 2, 1)

            self.CRb_df = DataFrame(CRb, columns=['Value'])
            self.CRb_df.index = [
                'UB_' + i for i in column_list_theta] + ['LB_' + i for i in column_list_theta]

            # CRb = numpy.array([*[1] * n_vars_theta, *[0] *
            #                    n_vars_theta]).reshape(n_vars_theta * 2, 1)

            return A, b, c, H, CRa, CRb, F, len(A_bal)

    def __repr__(self):
        return self.name
