"""Cost scenario data class
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
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

from ..components.location import Location
from ..components.network import Network
from ..components.process import ProcessMode, VaryingProcess
from ..components.resource import Resource, VaryingResource
from ..components.temporal_scale import TemporalScale


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
        network_scale_level (int, optional): scale for network decisions such as facility location. Defaults to 0.
        demand_scale_level (int, optional): scale for meeting specific demand for resource. Defaults to 0.
        cluster_wt (dict): cluster weights as a dictionary. {scale: int}. Defaults to None.
        label (str, optional): Longer descriptive label if required. Defaults to ''

    Example:
        The Scenario can be built over a single location. The network here is specified as a single Location. Considering scales (TemporalScale object for a year, [1, 365, 24]), scheduling, expenditure, and demand are met at an hourly level, and network at an annual level.

        >>> Current = Scenario(name= 'current', network= Goa, scales= scales, expenditure_scale_level= 2, scheduling_scale_level= 2, network_scale_level= 0, demand_scale_level= 2, label= 'Current Scenario')

        A multilocation Scenario needs a Network to be provided. Here, expenditure (on resource purchase) is determined at a daily scale. price_factor in the Location object needs to be commensurate in scale.

        >>> Future = Scenario(name= 'Future', network= System, scales= scales, expenditure_scale_level= 1, scheduling_scale_level= 2, network_scale_level= 0, demand_scale_level= 2, label= 'Future Scenario )
    """
    name: str
    scales: TemporalScale
    network: Union[Network, Location] = None
    purchase_scale_level: int = 0
    expenditure_scale_level: int = 0
    scheduling_scale_level: int = 0
    network_scale_level: int = 0
    demand_scale_level: int = 0
    cluster_wt: dict = None
    demand: Union[Dict[Location, Dict[Resource, float]], float] = None
    label: str = ''

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
            loc_res_dict (dict): A dictionary with Location-wise availability of Resource objects.
            loc_pro_dict (dict): A dictionary with Location-wise availability of Process objects.
            loc_mat_dict (dict): A dictionary with Location-wise availability of Material objects.
            price (dict): A dictionary with Location-wise cost of Resource objects
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
        """

        if isinstance(self.network, Location):
            self.transport_set = None
            self.source_locations = None
            self.sink_locations = None
            self.transport_dict = None
            self.transport_avail_dict = None
            self.trans_max = None
            self.trans_loss = None
            self.trans_cost = None
            self.trans_emit = None
            self.distance_dict = None
            self.location_set = {self.network}

        else:
            self.transport_set = set().union(*self.network.transport_dict.values())
            self.source_locations = self.network.source_locations
            self.sink_locations = self.network.sink_locations
            self.transport_dict = self.network.transport_dict
            self.transport_avail_dict = self.network.transport_avail_dict
            self.location_set = set(self.source_locations + self.sink_locations)
            self.trans_max = {j.name: j.trans_max for j in self.transport_set}
            self.trans_loss = {j.name: j.trans_loss for j in self.transport_set}
            self.trans_cost = {j.name: j.trans_cost for j in self.transport_set}
            self.trans_emit = {j.name: j.trans_emit for j in self.transport_set}
            self.distance_dict = self.network.distance_dict

        self.process_set = set().union(*[i.processes_full for i in self.location_set if i.processes_full is not None])
        self.resource_set = set().union(*[i.resources_full for i in self.location_set if i.resources is not None])
        self.material_set = set().union(*[i.materials for i in self.location_set if i.materials is not None])

        self.conversion = {i.name: {j.name: i.conversion[j] if j in i.conversion.keys() \
            else 0 for j in self.resource_set} for i in self.process_set if i.conversion is not None}

        self.prod_max = {i.name: i.prod_max for i in self.location_set}
        self.prod_min = {i.name: {j.name: j.prod_min for j in i.processes_full} for i in self.location_set}
        self.cons_max = {i.name: {j.name: j.cons_max for j in i.resources_full} for i in self.location_set}
        self.store_max = {i.name: {j.name: j.store_max for j in i.resources_full} for i in self.location_set}
        self.store_min = {i.name: {j.name: j.store_min for j in i.resources_full} for i in self.location_set}
        self.capacity_factor = {i.name: i.capacity_factor for i in self.location_set}
        self.price_factor = {i.name: i.price_factor for i in self.location_set}
        self.demand_factor = {i.name: i.demand_factor for i in self.location_set}
        self.capex_factor = {i.name: i.capex_factor for i in self.location_set}
        self.vopex_factor = {i.name: i.vopex_factor for i in self.location_set}
        self.fopex_factor = {i.name: i.fopex_factor for i in self.location_set}
        self.loc_res_dict = {i.name: {j.name for j in i.resources_full} for i in self.location_set}
        self.loc_pro_dict = {i.name: {j.name for j in i.processes_full} for i in self.location_set}
        self.loc_mat_dict = {i.name: {j.name for j in i.materials} for i in self.location_set}
        self.price = {i.name: i.resource_price for i in self.location_set}  # TODO change to be location wise
        self.capex_dict = {i.name: i.capex for i in self.process_set}
        self.fopex_dict = {i.name: i.fopex for i in self.process_set}
        self.vopex_dict = {i.name: i.vopex for i in self.process_set}
        self.incidental_dict = {i.name: i.incidental for i in self.process_set}
        self.land_dict = {i.name: i.land for i in self.process_set}
        self.material_gwp_dict = {i.name: {j.name: j.gwp for j in self.material_set} for i in self.location_set}
        self.resource_gwp_dict = {i.name: {j.name: j.gwp for j in self.resource_set} for i in self.location_set}
        self.process_gwp_dict = {i.name: {j.name: j.gwp for j in self.process_set} for i in self.location_set}
        self.land_cost_dict = {i.name: i.land_cost for i in self.location_set}
        self.fail_factor = {i.name: i.fail_factor for i in self.location_set}

        self.process_resource_dict = {i.name: i.resource_req for i in self.process_set}

        self.process_material_dict = {i.name: {j.name: i.material_cons[j] for j in i.material_cons.keys()} for i in
                                      self.process_set if i.material_cons is not None}

        multiconversion_dict = dict()
        for i in self.process_set:
            if i.processmode == ProcessMode.MULTI:
                multiconversion_dict[i.name] = {j: None for j in i.conversion.keys()}
                for k in list(multiconversion_dict[i.name].keys()):
                    multiconversion_dict[i.name][k] = {j.name: i.conversion[k][j] if j in i.conversion[k].keys() else 0
                                                       for j in self.resource_set}
            else:
                multiconversion_dict[i.name] = {0: None}
                multiconversion_dict[i.name][0] = {j.name: i.conversion[j] if j in i.conversion.keys() else 0 for j in
                                                   self.resource_set}

        self.multiconversion = multiconversion_dict

        self.mode_dict = {i.name: list(self.multiconversion[i.name].keys()) for i in self.process_set}

        self.set_dict = {
            'resources': [i.name for i in self.resource_set],
            'resources_nosell': [i.name for i in self.resource_set if i.sell is False],
            'resources_sell': [i.name for i in self.resource_set if i.sell is True],
            'resources_store': [i.name for i in self.resource_set if i.store_max > 0],
            'resources_purch': [i.name for i in self.resource_set if i.cons_max > 0],
            'resources_varying_demand': [i.name for i in self.resource_set if
                                         i.varying == VaryingResource.DETERMINISTIC_DEMAND],
            'resources_varying_price': [i.name for i in self.resource_set if
                                        i.varying == VaryingResource.DETERMINISTIC_PRICE],
            'resources_demand': [i.name for i in self.resource_set if i.demand is True],
            'resources_certain_price': [i.name for i in self.resource_set if (i.varying is None) and (i.cons_max > 0)],
            'resources_uncertain_price': [i.name for i in self.resource_set if
                                          i.varying == VaryingResource.UNCERTAIN_PRICE],
            'resources_certain_demand': [i.name for i in self.resource_set if
                                         (i.varying is None) and (i.demand is True)],
            'resources_uncertain_demand': [i.name for i in self.resource_set if
                                           i.varying == VaryingResource.UNCERTAIN_DEMAND],
            'processes': [i.name for i in self.process_set],
            'processes_full': list(self.conversion.keys()),
            'processes_varying': [i.name for i in self.process_set if
                                  i.varying == VaryingProcess.DETERMINISTIC_CAPACITY],
            'processes_failure': [i.name for i in self.process_set if i.p_fail is not None],
            'processes_materials': [i.name for i in self.process_set if i.material_cons is not None],
            'processes_storage': [i.name for i in self.process_set if i.conversion_discharge is not None],
            'processes_multim': [i.name for i in self.process_set if i.processmode == ProcessMode.MULTI],
            'processes_singlem': [i.name for i in self.process_set if
                                  (i.processmode == ProcessMode.SINGLE) or (i.processmode == ProcessMode.STORAGE)],
            'processes_certain_capacity': [i.name for i in self.process_set if i.varying is None],
            'processes_uncertain_capacity': [i.name for i in self.process_set if
                                             i.varying == VaryingProcess.UNCERTAIN_CAPACITY],
            'locations': [i.name for i in self.location_set],
            'materials': [i.name for i in self.material_set],
        }

        if self.source_locations is not None:
            self.set_dict['sources'] = [i.name for i in self.source_locations]
        else:
            self.set_dict['sources'] = []

        if self.sink_locations is not None:
            self.set_dict['sinks'] = [i.name for i in self.sink_locations]
        else:
            self.set_dict['sinks'] = []

        if self.material_set is not None:
            self.set_dict['materials'] = [i.name for i in self.material_set]
        else:
            self.set_dict['materials'] = []

        if self.transport_set is not None:
            self.set_dict['transports'] = [i.name for i in self.transport_set]
            self.set_dict['resources_trans'] = [i.name for i in set().union(*[i.resources for i in self.transport_set])]
        else:
            self.set_dict['transports'] = []
            self.set_dict['resources_trans'] = []

    def make_conversion_df(self) -> DataFrame:
        """makes a DataFrame of the conversion values

        Returns:
            DataFrame: DataFrame of conversion values 
        """
        return DataFrame.from_dict(self.conversion).transpose()

    def matrix_form(self):
        """returns matrices for the scenario.

        Returns:
            tuple: A, b, c, H, CRa, CRb, F
        """
        demand = self.demand
        if isinstance(demand, dict):
            if isinstance(list(demand.keys())[0], Location):
                self.demand = {i.name: {j.name: demand[i][j] for j in demand[i].keys()} for i in demand.keys()}
        print(demand)
        if len(self.location_set) > 1:
            print("can only do this for a single location scenario")
        else:
            location = list(self.location_set)[0].name

            # find number of different variables

            n_Inv = len(self.set_dict['resources_store'])
            n_Sf = len(self.set_dict['resources_certain_demand'])
            n_Cf = len(self.set_dict['resources_certain_price'])
            n_Pf = len(self.set_dict['processes_certain_capacity'])
            n_S = len(self.set_dict['resources_uncertain_demand'])
            n_C = len(self.set_dict['resources_uncertain_price'])
            n_P = len(self.set_dict['processes_uncertain_capacity'])
            n_bal = n_P + n_Pf

            n_vars_fix = n_Inv + n_Sf + n_Cf + n_Pf
            n_vars_theta = n_S + n_C + n_P
            n_vars = n_vars_fix + n_vars_theta

            # make b matrix
            # prod max has 0 because the default mode is 0
            b_bal = numpy.zeros((n_bal, 1))
            b_Inv = numpy.array([[self.store_max[location][i]] for i in self.set_dict['resources_store']])
            b_Sf = numpy.array([[-self.demand[location][i]] for i in self.set_dict['resources_certain_demand']])
            b_Cf = numpy.array([[self.cons_max[location][i]] for i in self.set_dict['resources_certain_price']])
            b_Pf = numpy.array([[self.prod_max[location][i][0]] for i in self.set_dict['processes_certain_capacity']])

            b_S = numpy.array([[-self.demand[location][i]] for i in self.set_dict['resources_uncertain_demand']])
            b_C = numpy.array([[self.cons_max[location][i]] for i in self.set_dict['resources_uncertain_price']])
            b_P = numpy.array([[self.prod_max[location][i][0]] for i in self.set_dict['processes_uncertain_capacity']])
            b_nn = numpy.zeros((n_vars, 1))

            b_list = [b_bal, b_Inv, b_Sf, b_Cf, b_Pf, b_S, b_C, b_P, b_nn]

            b = numpy.block([[i] for i in b_list if len(i) > 0])

            # make F matrix

            F = numpy.zeros((len(b), n_vars_theta))

            iter_ = 0
            for i in range(n_S):
                F[n_bal + n_vars_fix + iter_][i] = self.demand[location][self.set_dict['resources_uncertain_demand'][i]]
                iter_ += 1

            iter_ = 0
            for i in range(n_C):
                F[n_bal + n_vars_fix + n_S + iter_][n_S + i] = self.cons_max[location][
                    self.set_dict['resources_uncertain_price'][i]]
                iter_ += 1

            iter_ = 0
            for i in range(n_P):
                F[n_bal + n_vars_fix + n_S + n_C + iter_][n_S + n_C + i] = \
                self.prod_max[location][self.set_dict['processes_uncertain_capacity'][i]][
                    0]  # defaults to 0 as mode, using P_m instead of P
                iter_ += 1

            # make A matrix
            print(n_Inv, n_Sf, n_Cf, n_S, n_C)

            A_bal = numpy.diag([*[-1] * n_Inv, *[-1] * n_Sf, *[1] * n_Cf, *[-1] * n_S, *[1] * n_C])

            A_conv = numpy.array([[self.conversion[i][j] for j in self.conversion[i].keys()] for i in
                                  self.conversion.keys()]).transpose()

            A_diag = numpy.diag(
                [*[-1] * n_Inv, *[-1] * n_Sf, *[1] * n_Cf, *[1] * n_Pf, *[-1] * n_S, *[1] * n_C, *[1] * n_P])

            A_nn = numpy.eye(n_vars)

            print(A_bal)

            print(A_conv)

            print(A_diag)

            print(A_nn)

            A = numpy.block([[numpy.block([A_bal, A_conv])], [A_diag], [-A_nn]])

            # make c matrix

            c_Inv = numpy.zeros((n_Inv, 1))
            c_Sf = numpy.zeros((n_Sf, 1))
            c_Cf = numpy.zeros((n_Cf, 1))
            c_Pf = numpy.array([[self.capex_dict[i]] for i in self.set_dict['processes_certain_capacity']])

            c_S = numpy.zeros((n_S, 1))
            c_C = numpy.zeros((n_C, 1))
            c_P = numpy.array([[self.capex_dict[i]] for i in self.set_dict['processes_uncertain_capacity']])

            c_list = [c_Inv, c_Sf, c_Cf, c_Pf, c_S, c_C, c_P]
            c = numpy.block([[i] for i in c_list if len(i) > 0])

            # make H matrix

            H = numpy.zeros((A.shape[1], F.shape[1]))

            # make critical regions

            CRa = numpy.vstack((numpy.eye(n_vars_theta), -numpy.eye(n_vars_theta)))
            CRb = numpy.array([*[1] * n_vars_theta, *[0] * n_vars_theta]).reshape(n_vars_theta * 2, 1)

            return A, b, c, H, CRa, CRb, F

    def __repr__(self):
        return self.name
