"""Cost scenario data class
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2023, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "MIT"
__version__ = "1.0.5"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from dataclasses import dataclass
from typing import Dict, Union

import numpy
from pandas import DataFrame

from ..components.transport import VaryingTransport
from ..components.location import Location
from ..components.network import Network
from ..components.process import ProcessMode, VaryingProcess, CostDynamics
from ..components.resource import Resource, VaryingResource, Scope
# , VaryingEmission
from ..components.temporal_scale import TemporalScale
from ..model.bounds import CapacityBounds
from ..model.weights import EmissionWeights


@dataclass
class Scenario:
    """
    Scenario contains the network between location and all the data within.

    Args:
        name (str): name of scenario, short ones are better to deal with.
        scales (temporal_scale): scales of the problem
        network (Union[Network, Location]): network object with the locations, transport linakges, and processes (with resources and materials)
        purchase_scale_level (int, optional): scale for resource purchase. Defaults to 0.
        expenditure_scale_level (int, optional): scale for technology expenditure. Defaults to 0.
        scheduling_scale_level (int, optional): scale of production and inventory scheduling. Defaults to 0.
        availability_scale_level (int, optional): scale level for availability (resource). Defaults to 0
        capacity_scale_level (int, optional): scale level for capacity (process). Defaults to 0
        network_scale_level (int, optional): scale for network decisions such as facility location. Defaults to 0.
        demand_scale_level (int, optional): scale for meeting specific demand for resource. Defaults to 0.
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

        >>> Current = Scenario(name= 'current', network= Goa, scales= scales, expenditure_scale_level= 2, scheduling_scale_level= 2, network_scale_level= 0, demand_scale_level= 2, label= 'Current Scenario')

        A multilocation Scenario needs a Network to be provided. Here, expenditure (on resource purchase) is determined at a daily scale. price_factor in the Location object needs to be commensurate in scale.

        >>> Future = Scenario(name= 'Future', network= System, scales= scales, expenditure_scale_level= 1, scheduling_scale_level= 2, network_scale_level= 0, demand_scale_level= 2, label= 'Future Scenario' )
    """
    name: str
    scales: TemporalScale
    network: Union[Network, Location] = None
    purchase_scale_level: int = 0
    expenditure_scale_level: int = 0
    scheduling_scale_level: int = 0
    availability_scale_level: int = 0
    network_scale_level: int = 0
    demand_scale_level: int = 0
    capacity_scale_level: int = 0
    cluster_wt: dict = None
    demand: Union[Dict[Location, Dict[Resource, float]], float] = None
    label: str = ''
    capacity_bounds: CapacityBounds = None
    annualization_factor: float = 1
    demand_penalty: Dict[Location, Dict[Resource, float]] = None
    error: float = None
    rep_dict: dict = None
    emission_weights: EmissionWeights = None

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
            process_set (set): Set of all Process objects.
            resource_set (set): Set of all Resource objects.
            material_set (set): Set of all Material objects.
            conversion (dict): A dictionary with all conversion values for each Process.
            conversion_discharge (dict): A dictionary with all discharge conversions for Process of storage (ProcessMode.STORAGE) type.
            prod_max (dict): A dictionary with maximum production capacity per timeperiod in the network scale for each Process at each Location.
            prod_min (dict): A dictionary with minimum production capacity per timeperiod in the network scale for each Process at each Location.
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

        if isinstance(self.network, Location):
            self.transport_set = None
            self.source_locations = None
            self.sink_locations = None
            self.transport_dict = None
            self.transport_avail_dict = None
            self.trans_max = None
            self.trans_loss = None
            self.trans_capex = None
            self.trans_fopex = None
            self.trans_vopex = None
            self.trans_emission = None
            self.distance_dict = None
            self.location_set = {self.network}
            self.transport_capacity_factor = None
            self.transport_capex_factor = None
            self.transport_vopex_factor = None
            self.transport_fopex_factor = None
            self.transport_capacity_scale_level = None
            self.transport_capex_scale_level = None
            self.transport_vopex_scale_level = None
            self.transport_fopex_scale_level = None
            self.source_sink_resource_dict = None
        else:
            self.transport_set = set().union(*self.network.transport_dict.values())
            self.source_locations = self.network.source_locations
            self.sink_locations = self.network.sink_locations
            self.transport_dict = self.network.transport_dict
            self.transport_avail_dict = self.network.transport_avail_dict
            self.location_set = set(
                self.source_locations + self.sink_locations)
            self.trans_max = {j.name: j.trans_max for j in self.transport_set}
            self.trans_min = {j.name: j.trans_min for j in self.transport_set}
            self.trans_loss = {
                j.name: j.trans_loss for j in self.transport_set}
            self.trans_capex = {
                j.name: j.capex for j in self.transport_set}
            self.trans_vopex = {
                j.name: j.vopex for j in self.transport_set}
            self.trans_fopex = {
                j.name: j.fopex for j in self.transport_set}
            self.trans_emission = {
                j.name: j.emission for j in self.transport_set}
            self.distance_dict = self.network.distance_dict
            # self.transport_resource_dict = {i: None for i in self.transport_dict.keys()}
            self.location_transport_resource_dict = {i: {k.name: {
                l.name for l in k.resources} for k in j} for i, j in self.transport_dict.items()}
            self.resource_transport_dict = {}
            for key, value in {i.name: i.resources for i in self.transport_set}.items():
                for item in value:
                    if item in self.resource_transport_dict:
                        self.resource_transport_dict[item].append(key)
                    else:
                        self.resource_transport_dict[item] = [key]
            self.resource_transport_dict = {
                i.name: j for i, j in self.resource_transport_dict.items()}
            self.transport_resource_dict = {
                i.name: {j.name for j in i.resources} for i in self.transport_set}
            # for i,j in self.transport_dict.items():
            #     set_ = set()
            #     for k in j:
            #         set_ = set_.union(k.resources)
            #     self.transport_resource_dict[i] = {i.name for i in set_}

            self.transport_capacity_factor = self.network.transport_capacity_factor
            self.transport_capex_factor = self.network.transport_capex_factor
            self.transport_vopex_factor = self.network.transport_vopex_factor
            self.transport_fopex_factor = self.network.transport_fopex_factor
            self.transport_capacity_scale_level = self.network.transport_capacity_scale_level
            self.transport_capex_scale_level = self.network.transport_capex_scale_level
            self.transport_vopex_scale_level = self.network.transport_vopex_scale_level
            self.transport_fopex_scale_level = self.network.transport_fopex_scale_level
            self.source_sink_resource_dict = self.network.source_sink_resource_dict

        self.process_set = set().union(
            *[i.processes_full for i in self.location_set if i.processes_full is not None])
        self.resource_set = set().union(
            *[i.resources_full for i in self.location_set if i.resources is not None])
        self.material_set = set().union(
            *[i.materials for i in self.location_set if i.materials is not None])

        self.conversion = {i.name: {j.name: i.conversion[j] if j in i.conversion.keys(
        ) else 0 for j in self.resource_set} for i in self.process_set if i.conversion is not None}

        self.prod_max = {i.name: i.prod_max for i in self.location_set}
        self.prod_min = {i.name: i.prod_min for i in self.location_set}
        self.cons_max = {i.name: {
            j.name: j.cons_max for j in i.resources_full} for i in self.location_set}
        self.store_max = {i.name: {
            j.name: j.store_max for j in i.resources_full} for i in self.location_set}
        self.store_min = {i.name: {
            j.name: j.store_min for j in i.resources_full} for i in self.location_set}
        self.capacity_factor = {
            i.name: i.capacity_factor for i in self.location_set}
        self.price_factor = {i.name: i.price_factor for i in self.location_set}
        self.demand_factor = {
            i.name: i.demand_factor for i in self.location_set}
        self.capex_factor = {i.name: i.capex_factor for i in self.location_set}
        self.vopex_factor = {i.name: i.vopex_factor for i in self.location_set}
        self.fopex_factor = {i.name: i.fopex_factor for i in self.location_set}
        self.incidental_factor = {
            i.name: i.incidental_factor for i in self.location_set}
        self.availability_factor = {
            i.name: i.availability_factor for i in self.location_set}
        self.revenue_factor = {
            i.name: i.revenue_factor for i in self.location_set}
        self.location_resource_dict = {
            i.name: {j.name for j in i.resources_full} for i in self.location_set}
        self.location_process_dict = {
            i.name: {j.name for j in i.processes_full} for i in self.location_set}
        self.location_material_dict = {i.name: {j.name for j in i.materials}
                                       for i in self.location_set}
        # TODO change to be location wise
        self.price_dict = {i.name: i.resource_price for i in self.location_set}
        self.revenue_dict = {
            i.name: i.resource_revenue for i in self.location_set}
        self.capex_dict = {i.name: i.capex for i in self.process_set}
        self.fopex_dict = {i.name: i.fopex for i in self.process_set}
        self.vopex_dict = {i.name: i.vopex for i in self.process_set}
        self.incidental_dict = {i.name: i.incidental for i in self.process_set}
        self.land_dict = {i.name: i.land for i in self.process_set}
        self.material_gwp_dict = {
            i.name: {j.name: j.gwp for j in self.material_set} for i in self.location_set}
        self.material_odp_dict = {
            i.name: {j.name: j.odp for j in self.material_set} for i in self.location_set}
        self.material_acid_dict = {
            i.name: {j.name: j.acid for j in self.material_set} for i in self.location_set}
        self.material_eutt_dict = {
            i.name: {j.name: j.eutt for j in self.material_set} for i in self.location_set}
        self.material_eutf_dict = {
            i.name: {j.name: j.eutf for j in self.material_set} for i in self.location_set}
        self.material_eutm_dict = {
            i.name: {j.name: j.eutm for j in self.material_set} for i in self.location_set}
        self.resource_gwp_dict = {
            i.name: {j.name: j.gwp for j in self.resource_set} for i in self.location_set}
        self.resource_odp_dict = {
            i.name: {j.name: j.odp for j in self.resource_set} for i in self.location_set}
        self.resource_acid_dict = {
            i.name: {j.name: j.acid for j in self.resource_set} for i in self.location_set}
        self.resource_eutt_dict = {
            i.name: {j.name: j.eutt for j in self.resource_set} for i in self.location_set}
        self.resource_eutf_dict = {
            i.name: {j.name: j.eutf for j in self.resource_set} for i in self.location_set}
        self.resource_eutm_dict = {
            i.name: {j.name: j.eutm for j in self.resource_set} for i in self.location_set}
        self.process_gwp_dict = {
            i.name: {j.name: j.gwp for j in self.process_set} for i in self.location_set}
        self.process_odp_dict = {
            i.name: {j.name: j.odp for j in self.process_set} for i in self.location_set}
        self.process_acid_dict = {
            i.name: {j.name: j.acid for j in self.process_set} for i in self.location_set}
        self.process_eutt_dict = {
            i.name: {j.name: j.eutt for j in self.process_set} for i in self.location_set}
        self.process_eutf_dict = {
            i.name: {j.name: j.eutf for j in self.process_set} for i in self.location_set}
        self.process_eutm_dict = {
            i.name: {j.name: j.eutm for j in self.process_set} for i in self.location_set}
        self.land_cost_dict = {i.name: i.land_cost for i in self.location_set}
        self.fail_factor = {i.name: i.fail_factor for i in self.location_set}
        self.credit_dict = {i.name: {j.name: i.credit[j] for j in i.credit.keys(
        )} for i in self.location_set if i.credit is not None}

        # self.emission_dict = {i.name: {j.name: {l.name: {n.name: o for n, o in m.items(
        # )} if m is not None else None for l, m in k.items()} for j, k in i.emission_dict.items()} for i in self.location_set}
        self.process_resource_dict = {
            i.name: i.resource_req for i in self.process_set}
        # self.process_material_dict = {i.name: {j.name: i.material_cons[j] for j in i.material_cons.keys()} if i.material_cons is not None else None for i in
        #                               self.process_set}
        self.process_material_dict = {
            i.name: {j.name: i.material_cons[j] if j in i.material_cons.keys() else 0 for j in self.material_set} for i in self.process_set}

        self.process_material_mode_material_dict = {i.name: {j: {l.name: m for l, m in k.items(
        )} for j, k in i.material_cons.items()} for i in self.process_set}
        multiconversion_dict = dict()
        for i in self.process_set:
            if i.processmode == ProcessMode.MULTI:
                multiconversion_dict[i.name] = {
                    j: None for j in i.conversion.keys()}
                for k in list(multiconversion_dict[i.name].keys()):
                    multiconversion_dict[i.name][k] = {j.name: i.conversion[k][j] if j in i.conversion[k].keys() else 0
                                                       for j in self.resource_set}
            else:
                multiconversion_dict[i.name] = {0: None}
                multiconversion_dict[i.name][0] = {j.name: i.conversion[j] if j in i.conversion.keys() else 0 for j in
                                                   self.resource_set}

        self.multiconversion = multiconversion_dict

        self.mode_dict = {i.name: list(
            self.multiconversion[i.name].keys()) for i in self.process_set}

        if self.demand_penalty is not None:
            self.demand_penalty = {i.name: {j.name: self.demand_penalty[i][j] for j in self.demand_penalty[i].keys(
            )} for i in self.demand_penalty.keys()}

        df_capex = DataFrame.from_dict(
            self.capex_dict, orient='index', columns=['capex'])
        df_vopex = DataFrame.from_dict(
            self.vopex_dict, orient='index', columns=['vopex'])
        df_fopex = DataFrame.from_dict(
            self.fopex_dict, orient='index', columns=['fopex'])
        self.cost_df = df_capex.merge(df_vopex, left_index=True, right_index=True, how='inner').merge(
            df_fopex, left_index=True, right_index=True, how='inner')

        self.rate_max_dict = {i.name: i.rate_max for i in self.process_set}

        self.mode_ramp_dict = {i.name: i.mode_ramp for i in self.process_set}

        self.storage_cost_dict = {
            i.name: i.storage_cost_dict for i in self.location_set}

        process_material_modes = []
        for i in self.process_set:
            if i.material_cons is not None:

                process_material_modes = process_material_modes + \
                    [(i.name, j) for j in list(i.material_cons.keys())]
                if i.material_cons != {}:
                    self.process_material_modes = process_material_modes

                    self.process_material_modes_dict = {
                        i.name: i.material_modes for i in self.process_set}

        set_dict = {
            'resources': [i.name for i in self.resource_set],

            'resources_nosell': [i.name for i in self.resource_set if i.sell is False],
            'resources_sell': [i.name for i in self.resource_set if i.sell is True],
            
            'resources_sell_scope1': [i.name for i in self.resource_set if i.sell is True if i.scope == Scope.ONE],

            'resources_sell_scope2': [i.name for i in self.resource_set if i.sell is True if i.scope == Scope.TWO],

            'resources_store': [i.name for i in self.resource_set if i.store_max > 0],

            'resources_purch': [i.name for i in self.resource_set if i.cons_max > 0],

            'resources_purch_scope1' : [i.name for i in self.resource_set if i.cons_max > 0 if i.scope == Scope.ONE],
            
            'resources_purch_scope2' : [i.name for i in self.resource_set if i.cons_max > 0 if i.scope == Scope.TWO],

            'resources_varying_demand': [i.name for i in self.resource_set if
                                         VaryingResource.DETERMINISTIC_DEMAND in i.varying],
            'resources_certain_demand': [i.name for i in self.resource_set if
                                         VaryingResource.CERTAIN_DEMAND in i.varying],
            'resources_uncertain_demand': [i.name for i in self.resource_set if
                                           VaryingResource.UNCERTAIN_DEMAND in i.varying],

            # 'resources_varying_gwp': [i.name for i in self.resource_set if
            #                             VaryingEmission.DETERMINISTIC_GWP in i.varyinggwp],

            'resources_varying_price': [i.name for i in self.resource_set if
                                        VaryingResource.DETERMINISTIC_PRICE in i.varying],
            'resources_certain_price': [i.name for i in self.resource_set if
                                        VaryingResource.CERTAIN_PRICE in i.varying],
            'resources_uncertain_price': [i.name for i in self.resource_set if
                                          VaryingResource.UNCERTAIN_PRICE in i.varying],

            'resources_varying_revenue': [i.name for i in self.resource_set if
                                          VaryingResource.DETERMINISTIC_REVENUE in i.varying],
            'resources_certain_revenue': [i.name for i in self.resource_set if
                                          VaryingResource.CERTAIN_REVENUE in i.varying],
            'resources_uncertain_revenue': [i.name for i in self.resource_set if
                                            VaryingResource.UNCERTAIN_REVENUE in i.varying],

            'resources_varying_availability': [i.name for i in self.resource_set if
                                               VaryingResource.DETERMINISTIC_AVAILABILITY in i.varying],
            'resources_certain_availability': [i.name for i in self.resource_set if
                                               VaryingResource.CERTAIN_AVAILABILITY in i.varying],
            'resources_uncertain_availability': [i.name for i in self.resource_set if
                                                 VaryingResource.UNCERTAIN_AVAILABILITY in i.varying],

            'resources_demand': [i.name for i in self.resource_set if i.demand is True],

            'resources_implicit': [i.name for i in self.resource_set if VaryingResource.IMPLICIT in i.varying],

            'processes': [i.name for i in self.process_set],

            'processes_full': list(self.conversion.keys()),

            'processes_failure': [i.name for i in self.process_set if i.p_fail is not None],

            'processes_materials': [i.name for i in self.process_set if i.material_cons is not None],

            'processes_storage': [i.name for i in self.process_set if i.conversion_discharge is not None],

            'processes_multim': [i.name for i in self.process_set if i.processmode == ProcessMode.MULTI],
            'processes_singlem': [i.name for i in self.process_set if
                                  (i.processmode == ProcessMode.SINGLE) or (i.processmode == ProcessMode.STORAGE)],

            'processes_certain_capacity': [i.name for i in self.process_set if
                                           VaryingProcess.CERTAIN_CAPACITY in i.varying],
            'processes_varying_capacity': [i.name for i in self.process_set if
                                           VaryingProcess.DETERMINISTIC_CAPACITY in i.varying],
            'processes_uncertain_capacity': [i.name for i in self.process_set if
                                             VaryingProcess.UNCERTAIN_CAPACITY in i.varying],

            'processes_certain_expenditure': [i.name for i in self.process_set if
                                              VaryingProcess.CERTAIN_EXPENDITURE in i.varying],
            'processes_varying_expenditure': [i.name for i in self.process_set if
                                              VaryingProcess.DETERMINISTIC_EXPENDITURE in i.varying],
            'processes_uncertain_expenditure': [i.name for i in self.process_set if
                                                VaryingProcess.UNCERTAIN_EXPENDITURE in i.varying],

            'processes_segments': [i.name for i in self.process_set if i.cost_dynamics == CostDynamics.PWL],

            'locations': [i.name for i in self.location_set],
            'materials': [i.name for i in self.material_set],

            'process_material_modes': process_material_modes,

            'material_modes': [element for dictionary in list(i.material_modes for i in self.process_set) for element in dictionary]
        }

        self.varying_bounds_dict = {
            'demand': {i.name: i.varying_bounds for i in self.resource_set if VaryingResource.UNCERTAIN_DEMAND in i.varying},
            'availability': {i.name: i.varying_bounds for i in self.resource_set if VaryingResource.UNCERTAIN_AVAILABILITY in i.varying},
            'capacity': {i.name: i.varying_bounds for i in self.process_set if VaryingProcess.UNCERTAIN_CAPACITY in i.varying}
        }

        if self.source_locations is not None:
            set_dict['sources'] = [i.name for i in self.source_locations]
        else:
            set_dict['sources'] = []

        if self.sink_locations is not None:
            set_dict['sinks'] = [i.name for i in self.sink_locations]
        else:
            set_dict['sinks'] = []

        if self.material_set is not None:
            set_dict['materials'] = [i.name for i in self.material_set]
        else:
            set_dict['materials'] = []

        if self.transport_set is not None:
            set_dict['transports'] = [i.name for i in self.transport_set]
            set_dict['resources_trans'] = [i.name for i in set().union(
                *[i.resources for i in self.transport_set])]
        else:
            set_dict['transports'] = []
            set_dict['resources_trans'] = []

        self.set_dict = {x: sorted(set_dict[x]) for x in set_dict.keys()}

        if isinstance(self.network, Network):
            transport_set_dict = {
                'transports_certain_capacity': [i.name for i in self.transport_set if VaryingTransport.CERTAIN_CAPACITY in i.varying],
                'transports_certain_capex': [i.name for i in self.transport_set if VaryingTransport.CERTAIN_CAPEX in i.varying],
                'transports_certain_vopex': [i.name for i in self.transport_set if VaryingTransport.CERTAIN_VOPEX in i.varying],
                'transports_certain_fopex': [i.name for i in self.transport_set if VaryingTransport.CERTAIN_FOPEX in i.varying],

                'transports_uncertain_capacity': [i.name for i in self.transport_set if VaryingTransport.UNCERTAIN_CAPACITY in i.varying],
                'transports_uncertain_capex': [i.name for i in self.transport_set if VaryingTransport.UNCERTAIN_CAPEX in i.varying],
                'transports_uncertain_vopex': [i.name for i in self.transport_set if VaryingTransport.UNCERTAIN_VOPEX in i.varying],
                'transports_uncertain_fopex': [i.name for i in self.transport_set if VaryingTransport.UNCERTAIN_FOPEX in i.varying],

                'transports_varying_capacity': [i.name for i in self.transport_set if VaryingTransport.DETERMINISTIC_CAPACITY in i.varying],
                'transports_varying_capex': [i.name for i in self.transport_set if VaryingTransport.DETERMINISTIC_CAPEX in i.varying],
                'transports_varying_vopex': [i.name for i in self.transport_set if VaryingTransport.DETERMINISTIC_VOPEX in i.varying],
                'transports_varying_fopex': [i.name for i in self.transport_set if VaryingTransport.DETERMINISTIC_FOPEX in i.varying],
            }
            self.set_dict = {**self.set_dict, **transport_set_dict}

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
        if len(self.location_set) > 1:
            print("can only do this for a single location scenario")
        else:
            location = list(self.location_set)[0].name

            # find number of different variables
            # Inv - inventory
            # S - Sell/Discharge
            # C - Resource cost
            # A - Availability
            # P - Production

            n_Inv = len(self.set_dict['resources_store'])

            n_Sf = len(self.set_dict['resources_certain_demand'])
            n_S = len(self.set_dict['resources_uncertain_demand'])

            n_Af = len(self.set_dict['resources_certain_availability'])
            n_A = len(self.set_dict['resources_uncertain_availability'])

            n_Pf = len(self.set_dict['processes_certain_capacity'])
            n_P = len(self.set_dict['processes_uncertain_capacity'])

            n_Cf = len(self.set_dict['resources_certain_price'])
            n_C = len(self.set_dict['resources_uncertain_price'])

            n_I = len(self.set_dict['resources_implicit'])

            n_bal = n_P + n_Pf  # number of production processes for resource balance constraint

            # used to balance implicitly made resources
            n_bal2 = n_Inv + n_Sf + n_S + n_Af + n_A

            n_vars_fix = n_Inv + n_Sf + n_Af + n_Pf  # total number of fixed variables

            n_vars_theta = n_S + n_A + n_P  # total number of theta variables

            n_vars = n_vars_fix + n_vars_theta  # total number of variables

            print('The problem has the following variables:')
            print(f"Resource inventory level (Inv) x {n_Inv}")
            print(f"Exact resource discharge (Sf) x {n_Sf}")
            print(f"Uncertain resource discharge (S) x {n_S}")
            print(f"Exact resource availability (Af) x {n_Af}")
            print(f"Uncertain resource availability (A) x {n_A}")
            print(f"Exact resource price (Cf) x {n_Cf}")
            print(f"Uncertain resource price (C) x {n_C}")
            print(f"Exact process production (Pf) x {n_Pf}")
            print(f"Uncertain process production (P) x {n_P}")
            print(
                f" For a total of {n_vars} ({n_vars_fix} fixed, and {n_vars_theta} uncertain)")

            # *--------------------------------A--------------------------------------
            A_bal = numpy.diag(
                [*[1] * n_Inv, *[-1] * n_Sf, *[-1] * n_S,  *[1] * n_Af, *[1] * n_A])

            if n_I > 0:  # if implict variables present, add 0 stacks to matrix

                A_bal = numpy.vstack((A_bal, n_I*[[0]*(n_bal2)]))

            conversion_list = self.set_dict['resources_store'] + self.set_dict['resources_certain_demand'] + \
                self.set_dict['resources_uncertain_demand'] + \
                self.set_dict['resources_certain_availability'] + \
                self.set_dict['resources_uncertain_availability'] + \
                self.set_dict['resources_implicit']

            column_list_vars = [*['Inv_' + i for i in self.set_dict['resources_store']] +
                                ['Sf_' + i for i in self.set_dict['resources_certain_demand']] +
                                ['S_' + i for i in self.set_dict['resources_uncertain_demand']] +
                                ['Af_' + i for i in self.set_dict['resources_certain_availability']] +
                                ['A_' + i for i in self.set_dict['resources_uncertain_availability']] +
                                ['Pf_' + i for i in self.set_dict['processes_certain_capacity']] +
                                ['P_' + i for i in self.set_dict['processes_uncertain_capacity']]]

            A_conv = numpy.array([[self.conversion[i][j] for j in conversion_list] for i in
                                  sorted(self.conversion.keys())]).transpose()

            A_diag = numpy.diag(
                [*[1]*n_Inv, *[-1]*n_Sf, *[-1]*n_S,  *[1]*n_Af, *[1] * n_A, *[1]*n_Pf, *[1]*n_P])

            row_diag = [*['Inv_' + i + '(<)' for i in self.set_dict['resources_store']] +
                        ['Sf_' + i + '(>)' for i in self.set_dict['resources_certain_demand']] +
                        ['S_' + i + '(>)' for i in self.set_dict['resources_uncertain_demand']] +
                        ['Af_' + i + '(<)' for i in self.set_dict['resources_certain_availability']] +
                        ['A_' + i + '(<)' for i in self.set_dict['resources_uncertain_availability']] +
                        ['Pf_' + i + '(<)' for i in self.set_dict['processes_certain_capacity']] +
                        ['P_' + i + '(<)' for i in self.set_dict['processes_uncertain_capacity']]]

            row_NN = [*['NN_Inv_' + i + '(>)' for i in self.set_dict['resources_store']] +
                      ['NN_Sf_' + i + '(>)' for i in self.set_dict['resources_certain_demand']] +
                      ['NN_S_' + i + '(>)' for i in self.set_dict['resources_uncertain_demand']] +
                      ['NN_Af_' + i + '(>)' for i in self.set_dict['resources_certain_availability']] +
                      ['NN_A_' + i + '(>)' for i in self.set_dict['resources_uncertain_availability']] +
                      ['NN_Pf_' + i + '(>)' for i in self.set_dict['processes_certain_capacity']] +
                      ['NN_P_' + i + '(>)' for i in self.set_dict['processes_uncertain_capacity']]]

            row_bal = ['MB_' + i + '(=)' for i in self.set_dict['resources']]

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
            # b_S = numpy.array([[-self.demand[location][i]]
            #    for i in self.set_dict['resources_uncertain_demand']])  # uncertain demand
            b_Af = numpy.array([[self.cons_max[location][i]]
                                for i in self.set_dict['resources_certain_availability']])  # fixed availability bound
            b_A = numpy.array([[self.cons_max[location][i]]
                               for i in self.set_dict['resources_uncertain_availability']])  # uncertain availability

            b_Pf = numpy.array([[self.prod_max[location][i][0]]
                                for i in self.set_dict['processes_certain_capacity']])  # fixed production bound
            # b_P = numpy.array([[self.prod_max[location][i][0]]
            #                    for i in self.set_dict['processes_uncertain_capacity']])  # uncertain production

            # uncertain production
            b_P = numpy.array(
                [[0] for i in self.set_dict['processes_uncertain_capacity']])

            b_nn = numpy.zeros((n_vars, 1))  # non zero constraints

            b_list = [b_bal, b_Inv, b_Sf, b_S, b_Af, b_A, b_Pf, b_P, b_nn]

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
                n = n_Inv + n_Sf + n_S + n_Af
                F[n_bal3 + n + iter_][n_S + i] = self.cons_max[location][
                    self.set_dict['resources_uncertain_availability'][i]]
                iter_ += 1

            iter_ = 0
            for i in range(n_P):
                n = n_Inv + n_Sf + n_S + n_Af + n_A + n_Pf
                F[n_bal3 + n + iter_][n_S + n_A +
                                      i] = self.prod_max[location][self.set_dict['processes_uncertain_capacity'][i]][0]
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

            # c_Af = numpy.zeros((n_Af, 1))
            # c_A = numpy.zeros((n_A, 1))

            c_Cf = numpy.array([[self.price_dict[list(self.location_set)[0].name][i]]
                               for i in self.set_dict['resources_certain_price']])
            c_C = numpy.array([[self.price_dict[list(self.location_set)[0].name][i]]
                              for i in self.set_dict['resources_uncertain_price']])

            c_Pf = numpy.array([[self.vopex_dict[i]]
                                for i in self.set_dict['processes_certain_capacity']])
            c_P = numpy.array([[self.vopex_dict[i]]
                               for i in self.set_dict['processes_uncertain_capacity']])
            c_list = [c_Inv, c_Sf,  c_S, c_Cf,  c_C, c_Pf, c_P]
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
