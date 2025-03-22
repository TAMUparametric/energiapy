from pyomo.environ import *
import os
import sys
# sys.path.append('/scratch/user/shivam.vedant')
# sys.path.append('/scratch/user/shivam.vedant/src')
sys.path.append('../../../../src')

import mpisppy.utils.sputils as sputils
import matplotlib.pyplot as plt
from matplotlib import rc
import pandas
import random
import math
from itertools import product
from energiapy.components.temporal_scale import TemporalScale
from energiapy.components.resource import Resource, VaryingResource
from energiapy.components.process import Process, ProcessMode, VaryingProcess
from energiapy.components.location import Location
from energiapy.components.transport import Transport, VaryingTransport
from energiapy.components.network import Network
from energiapy.components.scenario import Scenario
from energiapy.components.result import Result
from energiapy.model.formulate import formulate, Constraints, Objective
from energiapy.plot import plot_results, plot_scenario, plot_location
from energiapy.model.solve import solve
from pyomo.environ import Param
from energiapy.utils.scale_utils import scale_pyomo_set
from energiapy.utils.scale_utils import scale_list, scale_tuple
from mpisppy.opt.ef import ExtensiveForm
from energiapy.model.constraints.constraints import make_constraint, Cons
from energiapy.model.formulate import constraint_export
import pickle
from pyomo.environ import value as pyoval
from functools import reduce

# _time_intervals = 7  # Number of time intervals in a planning horizon    (L_chi)
_exec_scenarios = 4  # Number of execution scenarios                     (chi)

M = 1e5  # Big M

def build_model(scen_df=pandas.DataFrame()):
    default_df = pandas.DataFrame(data=[1] * _exec_scenarios)
    scale_factor = 90

    # Define temporal scales
    scales = TemporalScale(discretization_list=[1, _exec_scenarios])

    # ======================================================================================================================
    # Declare resources/commodities
    # ======================================================================================================================
    com1_pur = Resource(name='com1_pur', cons_max=225*scale_factor, block={'imp': 1, 'urg': 1}, price=0.00,
                        label='Commodity 1 consumed from outside the system',
                        varying=[VaryingResource.DETERMINISTIC_AVAILABILITY])

    com1_in = Resource(name='com1_in', label='Commodity 1 received')
    com1_out = Resource(name='com1_out', label='Commodity 1 to be sent out')

    com1_loc1_out = Resource(name='com1_loc1_out', label='Commodity 1 sent out from location 1')
    com1_loc2_out = Resource(name='com1_loc2_out', label='Commodity 1 sent out from location 2')
    com1_loc3_out = Resource(name='com1_loc3_out', label='Commodity 1 sent out from location 3')
    com1_loc4_out = Resource(name='com1_loc4_out', label='Commodity 1 sent out from location 4')
    com1_loc5_out = Resource(name='com1_loc5_out', label='Commodity 1 sent out from location 5')
    com1_loc6_out = Resource(name='com1_loc6_out', label='Commodity 1 sent out from location 6')
    com1_loc7_out = Resource(name='com1_loc7_out', label='Commodity 1 sent out from location 7')

    com1_sold = Resource(name='com1_sold', revenue=0.00, demand=True, sell=True,
                         label='Commodity 1 sold to outside the system')

    # ======================================================================================================================
    # Declare processes/storage capacities
    # ======================================================================================================================
    com1_process_capacity = 500*scale_factor

    # prod_max = {0: 0.25*com1_process_capacity, 1: 0.5*com1_process_capacity, 2: 0.75*com1_process_capacity, 3: 0.95*com1_process_capacity, 4: com1_process_capacity}
    # prod_min = {0: 0, 1: 0.25*com1_process_capacity, 2: 0.5*com1_process_capacity, 3: 0.75*com1_process_capacity, 4: 0.95*com1_process_capacity}
    # rate_max = {0:1.25/2, 1: 1/2, 2: 0.75/2, 3: 0.5/2, 4: 0.25/2}
    # mode_ramp = {(0,1): 5, (1,2): 5}

    com1_procure = Process(name='procure com1', prod_max=com1_process_capacity, conversion={com1_pur: -1, com1_in: 1},
                           capex=25/scale_factor, vopex=0.01, prod_min=0.01, label='Procure com1')
    com1_sell = Process(name='sell com1', prod_max=com1_process_capacity, conversion={com1_out: -1, com1_sold: 1},
                        capex=0.1/scale_factor, vopex=0.01, prod_min=0.01, label='Sell com1')
    # com1_opt_procure = Process(name='procure optional com1', prod_max=75, conversion={com1_pur: -1, com1_in:1}, capex=10, vopex=0.1, prod_min=0.01, label='Procure optional com1')

    com1_receive_loc1 = Process(name='com1_receive_loc1', prod_max=com1_process_capacity,
                                conversion={com1_loc1_out: -1, com1_in: 1}, capex=0.1/scale_factor, vopex=0.01, prod_min=0.01,
                                label='Commodity 1 received from location 1')
    com1_receive_loc2 = Process(name='com1_receive_loc2', prod_max=com1_process_capacity,
                                conversion={com1_loc2_out: -1, com1_in: 1}, capex=0.1/scale_factor, vopex=0.01, prod_min=0.01,
                                label='Commodity 1 received from location 2')
    com1_receive_loc3 = Process(name='com1_receive_loc3', prod_max=com1_process_capacity,
                                conversion={com1_loc3_out: -1, com1_in: 1}, capex=0.1/scale_factor, vopex=0.01, prod_min=0.01,
                                label='Commodity 1 received from location 3')
    com1_receive_loc4 = Process(name='com1_receive_loc4', prod_max=com1_process_capacity,
                                conversion={com1_loc4_out: -1, com1_in: 1}, capex=0.1/scale_factor, vopex=0.01, prod_min=0.01,
                                label='Commodity 1 received from location 4')
    com1_receive_loc5 = Process(name='com1_receive_loc5', prod_max=com1_process_capacity,
                                conversion={com1_loc5_out: -1, com1_in: 1}, capex=0.1/scale_factor, vopex=0.01, prod_min=0.01,
                                label='Commodity 1 received from location 5')
    com1_receive_loc6 = Process(name='com1_receive_loc6', prod_max=com1_process_capacity,
                                conversion={com1_loc6_out: -1, com1_in: 1}, capex=0.1/scale_factor, vopex=0.01, prod_min=0.01,
                                label='Commodity 1 received from location 6')
    com1_receive_loc7 = Process(name='com1_receive_loc7', prod_max=com1_process_capacity,
                                conversion={com1_loc7_out: -1, com1_in: 1}, capex=0.1/scale_factor, vopex=0.01, prod_min=0.01,
                                label='Commodity 1 received from location 7')

    com1_process = Process(name='com1_process', prod_max=com1_process_capacity, conversion={com1_in: -1, com1_out: 1},
                           capex=5/scale_factor, vopex=0.01, prod_min=0.01, label='Process the commodity through the location',
                           varying=[VaryingProcess.DETERMINISTIC_CAPACITY])

    com1_store = Process(name='com1_store', prod_max=com1_process_capacity, capex=0.5/scale_factor, vopex=0.01, storage_capex=30/scale_factor, store_min=0.01,
                         store_max=200*scale_factor, prod_min=0.01, label="Storage process", storage=com1_in, storage_cost=0.02)

    com1_loc1_send = Process(name='com1_loc1_send', prod_max=com1_process_capacity,
                             conversion={com1_out: -1, com1_loc1_out: 1}, capex=0.1/scale_factor, vopex=0.01, prod_min=0.01,
                             label='Send commodity one from location 1')
    com1_loc2_send = Process(name='com1_loc2_send', prod_max=com1_process_capacity,
                             conversion={com1_out: -1, com1_loc2_out: 1}, capex=0.1/scale_factor, vopex=0.01, prod_min=0.01,
                             label='Send commodity one from location 2')
    com1_loc3_send = Process(name='com1_loc3_send', prod_max=com1_process_capacity,
                             conversion={com1_out: -1, com1_loc3_out: 1}, capex=0.1/scale_factor, vopex=0.01, prod_min=0.01,
                             label='Send commodity one from location 3')
    com1_loc4_send = Process(name='com1_loc4_send', prod_max=com1_process_capacity,
                             conversion={com1_out: -1, com1_loc4_out: 1}, capex=0.1/scale_factor, vopex=0.01, prod_min=0.01,
                             label='Send commodity one from location 4')
    com1_loc5_send = Process(name='com1_loc5_send', prod_max=com1_process_capacity,
                             conversion={com1_out: -1, com1_loc5_out: 1}, capex=0.1/scale_factor, vopex=0.01, prod_min=0.01,
                             label='Send commodity one from location 5')
    com1_loc6_send = Process(name='com1_loc6_send', prod_max=com1_process_capacity,
                             conversion={com1_out: -1, com1_loc6_out: 1}, capex=0.1/scale_factor, vopex=0.01, prod_min=0.01,
                             label='Send commodity one from location 6')
    com1_loc7_send = Process(name='com1_loc7_send', prod_max=com1_process_capacity,
                             conversion={com1_out: -1, com1_loc7_out: 1}, capex=0.1/scale_factor, vopex=0.01, prod_min=0.01,
                             label='Send commodity one from location 7')

    # ======================================================================================================================
    # Declare locations/warehouses
    # ======================================================================================================================
    loc1 = Location(name='loc1',
                    processes={com1_procure, com1_receive_loc2, com1_receive_loc3, com1_process, com1_store,
                               com1_loc1_send}, label="Location 1",
                    scales=scales, demand_scale_level=1, capacity_scale_level=1, availability_scale_level=1,
                    availability_factor={
                        com1_pur: scen_df[[('loc1', 'com1_pur')]] if ('loc1', 'com1_pur') in scen_df else default_df})

    loc2 = Location(name='loc2',
                    processes={com1_receive_loc1, com1_receive_loc4, com1_receive_loc5, com1_process, com1_store,
                               com1_loc2_send}, label="Location 2", scales=scales, demand_scale_level=1,
                    capacity_scale_level=1, availability_scale_level=1,
                    capacity_factor={com1_process: scen_df[[('loc2', 'com1_process')]] if ('loc2',
                                                                                           'com1_process') in scen_df else default_df})

    loc3 = Location(name='loc3',
                    processes={com1_receive_loc1, com1_receive_loc4, com1_process, com1_store, com1_loc3_send},
                    label="Location 3", scales=scales, demand_scale_level=1, capacity_scale_level=1,
                    availability_scale_level=1)

    loc4 = Location(name='loc4', processes={com1_receive_loc2, com1_receive_loc3, com1_receive_loc6, com1_receive_loc5,
                                            com1_receive_loc7, com1_process, com1_store, com1_loc4_send},
                    label="Location 4", scales=scales, demand_scale_level=1, capacity_scale_level=1,
                    availability_scale_level=1,
                    capacity_factor={com1_process: scen_df[[('loc4', 'com1_process')]] if ('loc4',
                                                                                           'com1_process') in scen_df else default_df})

    loc5 = Location(name='loc5',
                    processes={com1_receive_loc2, com1_receive_loc4, com1_receive_loc7, com1_process, com1_store,
                               com1_loc5_send, com1_sell}, label="Location 5", scales=scales, demand_scale_level=1,
                    capacity_scale_level=1, availability_scale_level=1)

    loc6 = Location(name='loc6', processes={com1_procure, com1_receive_loc4, com1_process, com1_store, com1_loc6_send},
                    label="Location 6", scales=scales, demand_scale_level=1, capacity_scale_level=1,
                    availability_scale_level=1,
                    availability_factor={
                        com1_pur: scen_df[[('loc6', 'com1_pur')]] if ('loc6', 'com1_pur') in scen_df else default_df})

    loc7 = Location(name='loc7',
                    processes={com1_receive_loc4, com1_receive_loc5, com1_process, com1_store, com1_loc7_send},
                    label="Location 7", scales=scales, demand_scale_level=1, capacity_scale_level=1,
                    availability_scale_level=1,
                    capacity_factor={com1_process: scen_df[[('loc7', 'com1_process')]] if ('loc7',
                                                                                           'com1_process') in scen_df else default_df})

    # ======================================================================================================================
    # Declare transport/trucks
    # ======================================================================================================================

    truck_cap12 = 280*scale_factor
    truck_cap13 = 270*scale_factor
    truck_cap24 = 450*scale_factor
    truck_cap25 = 270*scale_factor
    truck_cap34 = 270*scale_factor
    truck_cap45 = 500*scale_factor
    truck_cap47 = 360*scale_factor
    truck_cap64 = 450*scale_factor
    truck_cap75 = 360*scale_factor

    truck12 = Transport(name='truck12', resources={com1_loc1_out}, trans_max=truck_cap12,
                        label='Truck from location 1 to 2', capex=0.5/scale_factor, vopex=0.05, trans_min=0.01, varying=[VaryingTransport.DETERMINISTIC_CAPACITY])
    # truck21 = Transport(name='truck21', resources={com1_loc2_out}, trans_max=truck_cap12,
    #                     label='Truck from location 2 to 1', capex=0.0001, vopex=0.05, trans_min=0.01)

    truck13 = Transport(name='truck13', resources={com1_loc1_out}, trans_max=truck_cap13,
                        label='Truck from location 1 to 3', capex=0.3/scale_factor, vopex=0.03, trans_min=0.01, varying=[VaryingTransport.DETERMINISTIC_CAPACITY])
    # truck31 = Transport(name='truck31', resources={com1_loc3_out}, trans_max=truck_cap13,
    #                     label='Truck from location 3 to 1', capex=0.0001, vopex=0.03, trans_min=0.01)

    truck24 = Transport(name='truck24', resources={com1_loc2_out}, trans_max=truck_cap24,
                        label='Truck from location 2 to 4', capex=0.5/scale_factor, vopex=0.05, trans_min=0.01, varying=[VaryingTransport.DETERMINISTIC_CAPACITY])
    # truck42 = Transport(name='truck42', resources={com1_loc4_out}, trans_max=truck_cap24,
    #                     label='Truck from location 4 to 2', capex=0.0001, vopex=0.05, trans_min=0.01)

    truck25 = Transport(name='truck25', resources={com1_loc2_out}, trans_max=truck_cap25,
                        label='Truck from location 2 to 5', capex=0.3/scale_factor, vopex=0.03, trans_min=0.01, varying=[VaryingTransport.DETERMINISTIC_CAPACITY])
    # truck52 = Transport(name='truck52', resources={com1_loc5_out}, trans_max=truck_cap25,
    #                     label='Truck from location 5 to 2', capex=0.0001, vopex=0.03, trans_min=0.01)

    truck34 = Transport(name='truck34', resources={com1_loc3_out}, trans_max=truck_cap34,
                        label='Truck from location 3 to 4', capex=0.2/scale_factor, vopex=0.02, trans_min=0.01, varying=[VaryingTransport.DETERMINISTIC_CAPACITY])
    # truck43 = Transport(name='truck43', resources={com1_loc4_out}, trans_max=truck_cap34,
    #                     label='Truck from location 4 to 3', capex=0.0001, vopex=0.02, trans_min=0.01)

    truck45 = Transport(name='truck45', resources={com1_loc4_out}, trans_max=truck_cap45,
                        label='Truck from location 4 to 5', capex=1/scale_factor, vopex=0.1, trans_min=0.01, varying=[VaryingTransport.DETERMINISTIC_CAPACITY])
    # truck54 = Transport(name='truck54', resources={com1_loc5_out}, trans_max=truck_cap45,
    #                     label='Truck from location 5 to 4', capex=0.0001, vopex=0.1, trans_min=0.01)

    truck47 = Transport(name='truck47', resources={com1_loc4_out}, trans_max=truck_cap47,
                        label='Truck from location 4 to 7', capex=0.4/scale_factor, vopex=0.04, trans_min=0.01, varying=[VaryingTransport.DETERMINISTIC_CAPACITY])
    # truck74 = Transport(name='truck74', resources={com1_loc7_out}, trans_max=truck_cap47,
    #                     label='Truck from location 7 to 4', capex=0.0001, vopex=0.04, trans_min=0.01)

    truck64 = Transport(name='truck64', resources={com1_loc6_out}, trans_max=truck_cap64,
                        label='Truck from location 6 to 4', capex=0.5/scale_factor, vopex=0.05, trans_min=0.01, varying=[VaryingTransport.DETERMINISTIC_CAPACITY])
    # truck46 = Transport(name='truck46', resources={com1_loc4_out}, trans_max=truck_cap64,
    #                     label='Truck from location 4 to 6', capex=0.0001, vopex=0.05, trans_min=0.01)

    truck75 = Transport(name='truck75', resources={com1_loc7_out}, trans_max=truck_cap75,
                        label='Truck from location 7 to 5', capex=0.4/scale_factor, vopex=0.04, trans_min=0.01, varying=[VaryingTransport.DETERMINISTIC_CAPACITY])
    # truck57 = Transport(name='truck57', resources={com1_loc5_out}, trans_max=truck_cap75,
    #                     label='Truck from location 5 to 7', capex=0.0001, vopex=0.04, trans_min=0.01)

    # ======================================================================================================================
    # Declare network
    # ======================================================================================================================

    transport_matrix = [
        [[], [truck12], [truck13], [], [], [], []],  # source: location 1
        [[], [], [], [truck24], [truck25], [], []],  # source: location 2
        [[], [], [], [truck34], [], [], []],  # source: location 3
        [[], [], [], [], [truck45], [], [truck47]],  # source: location 4
        [[], [], [], [], [], [], []],  # source: location 5
        [[], [], [], [truck64], [], [], []],  # source: location 6
        [[], [], [], [], [truck75], [], []]  # source: location 7
    ]

    # transport_matrix = [
    #     [[], [truck12], [truck13], [], [], [], []],  # source: location 1
    #     [[truck21], [], [], [truck24], [truck25], [], []],  # source: location 2
    #     [[truck31], [], [], [truck34], [], [], []],  # source: location 3
    #     [[], [truck42], [truck43], [], [truck45], [truck46], [truck47]],  # source: location 4
    #     [[], [truck52], [], [truck54], [], [], [truck57]],  # source: location 5
    #     [[], [], [], [truck64], [], [], []],  # source: location 6
    #     [[], [], [], [truck74], [truck75], [], []]  # source: location 7
    # ]

    distance_matrix = [
        [0, 55, 196, M, M, M, M],
        [55, 0, M, 163, 112, M, 134],
        [196, M, 0, 63, M, M, M],
        [M, 163, 63, 0, 95, 117, 88],
        [M, 112, M, 95, 0, M, 134],
        [M, M, M, 117, M, 0, M],
        [M, 134, M, 88, 134, M, 0]
    ]

    locset = [loc1, loc2, loc3, loc4, loc5, loc6, loc7]

    sources = locset
    sinks = locset

    network = Network(name='Network', scales=scales, source_locations=sources, sink_locations=sinks,
                      transport_matrix=transport_matrix, distance_matrix=distance_matrix, transport_capacity_scale_level=1,
                      transport_capacity_factor={(loc1, loc2): {truck12: scen_df[[('trans12', 'com1_loc1_out')]] if ('trans12', 'com1_loc1_out') in scen_df else default_df},
                                                 (loc1, loc3): {truck13: scen_df[[('trans13', 'com1_loc1_out')]] if ('trans13', 'com1_loc1_out') in scen_df else default_df},
                                                 (loc2, loc4): {truck24: scen_df[[('trans24', 'com1_loc2_out')]] if ('trans24', 'com1_loc2_out') in scen_df else default_df},
                                                 (loc2, loc5): {truck25: scen_df[[('trans25', 'com1_loc2_out')]] if ('trans25', 'com1_loc2_out') in scen_df else default_df},
                                                 (loc3, loc4): {truck34: scen_df[[('trans34', 'com1_loc3_out')]] if ('trans34', 'com1_loc3_out') in scen_df else default_df},
                                                 (loc4, loc5): {truck45: scen_df[[('trans45', 'com1_loc4_out')]] if ('trans45', 'com1_loc4_out') in scen_df else default_df},
                                                 (loc4, loc7): {truck47: scen_df[[('trans47', 'com1_loc4_out')]] if ('trans47', 'com1_loc4_out') in scen_df else default_df},
                                                 (loc6, loc4): {truck64: scen_df[[('trans64', 'com1_loc6_out')]] if ('trans64', 'com1_loc6_out') in scen_df else default_df},
                                                 (loc7, loc5): {truck75: scen_df[[('trans75', 'com1_loc7_out')]] if ('trans75', 'com1_loc7_out') in scen_df else default_df},
                                                 })

    # ======================================================================================================================
    # Declare scenario
    # ======================================================================================================================

    daily_demand = 400*scale_factor
    demand_penalty = 20

    demand_dict = {i: {com1_sold: daily_demand} if i == loc5 else {com1_sold: 0} for i in locset}
    demand_penalty_dict = {i: {com1_sold: demand_penalty} if i == loc5 else {com1_sold: 0} for i in locset}

    scenario = Scenario(name='scenario', scales=scales, scheduling_scale_level=1, network_scale_level=0,
                        purchase_scale_level=1, availability_scale_level=1, demand_scale_level=1,
                        capacity_scale_level=1, network=network, demand=demand_dict, demand_penalty=demand_penalty_dict,
                        label='Stochastic scenario with Multiple Locations')

    if scen_df.empty:
        # ======================================================================================================================
        # Declare problem
        # ======================================================================================================================

        problem_mincost = formulate(scenario=scenario,
                                    constraints={Constraints.COST, Constraints.TRANSPORT, Constraints.RESOURCE_BALANCE,
                                                 Constraints.INVENTORY, Constraints.PRODUCTION, Constraints.DEMAND,
                                                 Constraints.NETWORK},
                                    demand_sign='eq', objective=Objective.COST_W_DEMAND_PENALTY)

        scale_iter = scale_tuple(instance=problem_mincost, scale_levels=scenario.network_scale_level + 1)
        capex_process = sum(problem_mincost.Capex_network[scale_] for scale_ in scale_iter)
        cost_trans_capex = sum(problem_mincost.Capex_transport_network[scale_] for scale_ in scale_iter)

        problem_mincost.first_stage_cost = capex_process + cost_trans_capex

        return scenario, problem_mincost

    else:
        return scenario

def build_smodel(scen_df=pandas.DataFrame()):

    scenario = build_model(scen_df)
    # ======================================================================================================================
    # Declare problem
    # ======================================================================================================================

    problem_mincost = formulate(scenario=scenario,
                                constraints={Constraints.COST, Constraints.TRANSPORT, Constraints.RESOURCE_BALANCE,
                                             Constraints.INVENTORY, Constraints.PRODUCTION, Constraints.DEMAND,
                                             Constraints.NETWORK},
                                demand_sign='eq', objective=Objective.COST_W_DEMAND_PENALTY)

    scale_iter = scale_tuple(instance=problem_mincost, scale_levels=scenario.network_scale_level + 1)
    capex_process = sum(problem_mincost.Capex_network[scale_] for scale_ in scale_iter)
    cost_trans_capex = sum(problem_mincost.Capex_transport_network[scale_] for scale_ in scale_iter)

    problem_mincost.first_stage_cost = capex_process + cost_trans_capex

    return scenario, problem_mincost


def find_common_substring(lst):
    # Split each string into substrings and create sets
    substring_sets = [set(item.split()) for item in lst]

    # Find the intersection of all sets to get common substrings
    common_substrings = reduce(lambda a, b: a & b, substring_sets)

    return common_substrings


def filter_scenarios():
    # Initialize the result dictionary
    result = {}

    # Step 1: Iterate over the original data
    for scenario, data in PI_load_dict.items():
        x_val = data['Demand_penalty_network'][('com1_sold', 0)]
        obj_val = data['objective']

        # Step 2: Check if x_val is already a key in the result
        if x_val not in result:
            result[x_val] = {'count': 0, 'objectives': {}}

        # Increment the count for the x value
        result[x_val]['count'] += 1

        # Step 3: Check if obj_val is already a key under the 'objectives' for this x
        if obj_val not in result[x_val]['objectives']:
            result[x_val]['objectives'][obj_val] = {'scenarios': [], 'count': 0}

        # Add the scenario to the list and increment the count for the objective
        result[x_val]['objectives'][obj_val]['scenarios'].append(scenario)
        result[x_val]['objectives'][obj_val]['count'] += 1

    # Step 4: Sort the result by x values (in decreasing order) and objectives (in decreasing order)
    sorted_result = {
        x_val: {
            'count': result[x_val]['count'],
            'count_obj': len(result[x_val]['objectives']),
            'objectives': {
                obj_val: result[x_val]['objectives'][obj_val]
                for obj_val in sorted(result[x_val]['objectives'].keys(), reverse=True)
            }
        }
        for x_val in sorted(result.keys(), reverse=True)
    }

    return sorted_result


def pick_scenarios(sorted_dict, n):
    selected_scenarios = {}
    total_selected = 0

    # Iterate over sorted x values
    for x_val, x_data in sorted_dict.items():
        if total_selected >= n:
            break  # Stop if we have selected enough scenarios

        # Iterate over sorted objective values within each x
        for obj_val, obj_data in x_data['objectives'].items():
            if total_selected >= n:
                break  # Stop if we have selected enough scenarios

            # Randomly select from the list of scenarios if there are multiple
            scenarios_to_choose = obj_data['scenarios']
            num_to_pick = min(len(scenarios_to_choose), 1)
            chosen_scenarios = random.sample(scenarios_to_choose, num_to_pick)

            # Add the selected scenarios to the result
            if x_val not in selected_scenarios:
                selected_scenarios[x_val] = {}

            if obj_val not in selected_scenarios[x_val]:
                selected_scenarios[x_val][obj_val] = {}

            for scenario in chosen_scenarios:
                selected_scenarios[x_val][obj_val][scenario] = {
                    'prob': scenario_load_dict[scenario]['prob'],
                    'factor': scenario_load_dict[scenario]['factor'].copy()
                }
                total_selected += 1

                if total_selected >= n:
                    break  # Stop if we have selected enough scenarios

    return selected_scenarios


def sum_probabilities(d):
    total_prob = 0

    def recursive_sum(current_dict):
        nonlocal total_prob
        for key, value in current_dict.items():
            if isinstance(value, dict):
                # Recursively traverse if it's still a dictionary
                recursive_sum(value)
            elif key == 'prob':
                # Add the probability value
                total_prob += value

    recursive_sum(d)
    return total_prob

def scenario_creator(scen_name, **kwargs):
    scen_dict = kwargs.get('scenario_dict')
    scen, model = build_smodel(scen_df=scen_dict[scen_name]['factor'])
    sputils.attach_root_node(model, model.first_stage_cost,
                             [model.X_P, model.Cap_P, model.X_S, model.Cap_S, model.X_F, model.Cap_F])
    model._mpisppy_probability = scen_dict[scen_name]['prob']
    return model

if __name__ == '__main__':

    scenarios_to_select = 10
    random.seed(2)

    solver_options = {
        'MIPGap': 0.005,
        # 'TimeLimit': 60 * 15,
        'Heuristics': 0.20
    }

    with open('scenario_dict.pkl', 'rb') as file:
        scenario_load_dict = pickle.load(file)

    with open('sorted_result.pkl', 'rb') as file:
        sorted_result = pickle.load(file)

    scenario_load_names = list(scenario_load_dict.keys())

    selected_scenarios = pick_scenarios(sorted_result, scenarios_to_select)

    norm_factor = sum_probabilities(selected_scenarios)
    selected_scenario_dict = {
        k: {
            'prob': scenario_data['prob'] / norm_factor,
            'factor': scenario_data['factor'].copy()
        }
        for i, inner_dict in selected_scenarios.items()
        for j, sub_dict in inner_dict.items()
        for k, scenario_data in sub_dict.items()
    }

    selected_scenario_names = list(selected_scenario_dict.keys())
    print(f'Number of scenarios considered: {len(selected_scenario_names)}')

    prob_select = sum_probabilities(selected_scenario_dict)
    print(f'Sum of probabilities of considered scenarios: {prob_select}')

    options = {"solver": "gurobi"}
    scenario_creator_kwargs = {'scenario_dict': selected_scenario_dict}
    ef_UI = ExtensiveForm(options, selected_scenario_names, scenario_creator,
                          scenario_creator_kwargs=scenario_creator_kwargs)
    results = ef_UI.solve_extensive_form(solver_options=solver_options)

    exCost_UI = ef_UI.get_objective_value()

    ssoln_dict = ef_UI.get_root_solution()
    ssoln_dict['exCost_UI'] = exCost_UI
    with open(f'ssoln_IE_MultiLoc_stochastic_{scenarios_to_select}_.pkl', 'wb') as file:
        pickle.dump(ssoln_dict, file)
