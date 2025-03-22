from pyomo.environ import *
import os
import sys
sys.path.append('/scratch/user/shivam.vedant')
sys.path.append('/scratch/user/shivam.vedant/src')
sys.path.append('/scratch/user/shivam.vedant/Scripts/TSSP/AIChE2024/min_p')
# sys.path.append('../../../../src')

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
import time

# _time_intervals = 7  # Number of time intervals in a planning horizon    (L_chi)
_exec_scenarios = 4  # Number of execution scenarios                     (chi)

M = 1e5  # Big M

def pick_scenario_with_highest_probability(scenario_list, scenario_dict):
    # Filter scenarios in the list that are present in the dictionary
    valid_scenarios = [(s, scenario_dict[s]['prob']) for s in scenario_list if s in scenario_dict]

    # Find the maximum probability among valid scenarios
    max_prob = min(valid_scenarios, key=lambda x: x[1], default=(None, -1))[1]

    # Collect scenarios with the maximum probability
    highest_prob_scenarios = [s for s, p in valid_scenarios if p == max_prob]

    return random.choice(highest_prob_scenarios) if highest_prob_scenarios else None

def pick_scenarios(sorted_dict, n, scenario_dict):
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

            # Get the list of scenarios for the current objective
            scenarios_to_choose = obj_data['scenarios']

            # Choose the scenario with the highest probability using the previous logic
            chosen_scenario = pick_scenario_with_highest_probability(scenarios_to_choose, scenario_dict)

            # Add the selected scenario to the result
            if chosen_scenario:
                if x_val not in selected_scenarios:
                    selected_scenarios[x_val] = {}

                if obj_val not in selected_scenarios[x_val]:
                    selected_scenarios[x_val][obj_val] = {}

                selected_scenarios[x_val][obj_val][chosen_scenario] = {
                    'prob': scenario_dict[chosen_scenario]['prob'],
                    'factor': scenario_dict[chosen_scenario]['factor'].copy()
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


def build_model(scen_df=pandas.DataFrame()):
    default_df = pandas.DataFrame(data=[1] * _exec_scenarios)
    scale_factor = 90

    # Define temporal scales
    scales = TemporalScale(discretization_list=[1, _exec_scenarios])

    # ======================================================================================================================
    # Declare resources/commodities
    # ======================================================================================================================
    com1_pur = Resource(name='com1_pur', cons_max=225 * scale_factor, block={'imp': 1, 'urg': 1}, price=0.00,
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
    com1_process_capacity = 500 * scale_factor

    # prod_max = {0: 0.25*com1_process_capacity, 1: 0.5*com1_process_capacity, 2: 0.75*com1_process_capacity, 3: 0.95*com1_process_capacity, 4: com1_process_capacity}
    # prod_min = {0: 0, 1: 0.25*com1_process_capacity, 2: 0.5*com1_process_capacity, 3: 0.75*com1_process_capacity, 4: 0.95*com1_process_capacity}
    # rate_max = {0:1.25/2, 1: 1/2, 2: 0.75/2, 3: 0.5/2, 4: 0.25/2}
    # mode_ramp = {(0,1): 5, (1,2): 5}

    com1_procure = Process(name='procure com1', prod_max=com1_process_capacity, conversion={com1_pur: -1, com1_in: 1},
                           capex=25 / scale_factor, vopex=0.01, prod_min=0.01, label='Procure com1')
    com1_sell = Process(name='sell com1', prod_max=com1_process_capacity, conversion={com1_out: -1, com1_sold: 1},
                        capex=0.1 / scale_factor, vopex=0.01, prod_min=0.01, label='Sell com1')
    # com1_opt_procure = Process(name='procure optional com1', prod_max=75, conversion={com1_pur: -1, com1_in:1}, capex=10, vopex=0.1, prod_min=0.01, label='Procure optional com1')

    com1_receive_loc1 = Process(name='com1_receive_loc1', prod_max=com1_process_capacity,
                                conversion={com1_loc1_out: -1, com1_in: 1}, capex=0.1 / scale_factor, vopex=0.01,
                                prod_min=0.01,
                                label='Commodity 1 received from location 1')
    com1_receive_loc2 = Process(name='com1_receive_loc2', prod_max=com1_process_capacity,
                                conversion={com1_loc2_out: -1, com1_in: 1}, capex=0.1 / scale_factor, vopex=0.01,
                                prod_min=0.01,
                                label='Commodity 1 received from location 2')
    com1_receive_loc3 = Process(name='com1_receive_loc3', prod_max=com1_process_capacity,
                                conversion={com1_loc3_out: -1, com1_in: 1}, capex=0.1 / scale_factor, vopex=0.01,
                                prod_min=0.01,
                                label='Commodity 1 received from location 3')
    com1_receive_loc4 = Process(name='com1_receive_loc4', prod_max=com1_process_capacity,
                                conversion={com1_loc4_out: -1, com1_in: 1}, capex=0.1 / scale_factor, vopex=0.01,
                                prod_min=0.01,
                                label='Commodity 1 received from location 4')
    com1_receive_loc5 = Process(name='com1_receive_loc5', prod_max=com1_process_capacity,
                                conversion={com1_loc5_out: -1, com1_in: 1}, capex=0.1 / scale_factor, vopex=0.01,
                                prod_min=0.01,
                                label='Commodity 1 received from location 5')
    com1_receive_loc6 = Process(name='com1_receive_loc6', prod_max=com1_process_capacity,
                                conversion={com1_loc6_out: -1, com1_in: 1}, capex=0.1 / scale_factor, vopex=0.01,
                                prod_min=0.01,
                                label='Commodity 1 received from location 6')
    com1_receive_loc7 = Process(name='com1_receive_loc7', prod_max=com1_process_capacity,
                                conversion={com1_loc7_out: -1, com1_in: 1}, capex=0.1 / scale_factor, vopex=0.01,
                                prod_min=0.01,
                                label='Commodity 1 received from location 7')

    com1_process = Process(name='com1_process', prod_max=com1_process_capacity, conversion={com1_in: -1, com1_out: 1},
                           capex=5 / scale_factor, vopex=0.01, prod_min=0.01,
                           label='Process the commodity through the location',
                           varying=[VaryingProcess.DETERMINISTIC_CAPACITY])

    com1_store = Process(name='com1_store', prod_max=com1_process_capacity, capex=0.5 / scale_factor, vopex=0.01,
                         storage_capex=30 / scale_factor, store_min=0.01,
                         store_max=200 * scale_factor, prod_min=0.01, label="Storage process", storage=com1_in,
                         storage_cost=0.02)

    com1_loc1_send = Process(name='com1_loc1_send', prod_max=com1_process_capacity,
                             conversion={com1_out: -1, com1_loc1_out: 1}, capex=0.1 / scale_factor, vopex=0.01,
                             prod_min=0.01,
                             label='Send commodity one from location 1')
    com1_loc2_send = Process(name='com1_loc2_send', prod_max=com1_process_capacity,
                             conversion={com1_out: -1, com1_loc2_out: 1}, capex=0.1 / scale_factor, vopex=0.01,
                             prod_min=0.01,
                             label='Send commodity one from location 2')
    com1_loc3_send = Process(name='com1_loc3_send', prod_max=com1_process_capacity,
                             conversion={com1_out: -1, com1_loc3_out: 1}, capex=0.1 / scale_factor, vopex=0.01,
                             prod_min=0.01,
                             label='Send commodity one from location 3')
    com1_loc4_send = Process(name='com1_loc4_send', prod_max=com1_process_capacity,
                             conversion={com1_out: -1, com1_loc4_out: 1}, capex=0.1 / scale_factor, vopex=0.01,
                             prod_min=0.01,
                             label='Send commodity one from location 4')
    com1_loc5_send = Process(name='com1_loc5_send', prod_max=com1_process_capacity,
                             conversion={com1_out: -1, com1_loc5_out: 1}, capex=0.1 / scale_factor, vopex=0.01,
                             prod_min=0.01,
                             label='Send commodity one from location 5')
    com1_loc6_send = Process(name='com1_loc6_send', prod_max=com1_process_capacity,
                             conversion={com1_out: -1, com1_loc6_out: 1}, capex=0.1 / scale_factor, vopex=0.01,
                             prod_min=0.01,
                             label='Send commodity one from location 6')
    com1_loc7_send = Process(name='com1_loc7_send', prod_max=com1_process_capacity,
                             conversion={com1_out: -1, com1_loc7_out: 1}, capex=0.1 / scale_factor, vopex=0.01,
                             prod_min=0.01,
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

    truck_cap12 = 280 * scale_factor
    truck_cap13 = 270 * scale_factor
    truck_cap24 = 450 * scale_factor
    truck_cap25 = 270 * scale_factor
    truck_cap34 = 270 * scale_factor
    truck_cap45 = 500 * scale_factor
    truck_cap47 = 360 * scale_factor
    truck_cap64 = 450 * scale_factor
    truck_cap75 = 360 * scale_factor

    truck12 = Transport(name='truck12', resources={com1_loc1_out}, trans_max=truck_cap12,
                        label='Truck from location 1 to 2', capex=0.5 / scale_factor, vopex=0.05, trans_min=0.01,
                        varying=[VaryingTransport.DETERMINISTIC_CAPACITY])
    # truck21 = Transport(name='truck21', resources={com1_loc2_out}, trans_max=truck_cap12,
    #                     label='Truck from location 2 to 1', capex=0.0001, vopex=0.05, trans_min=0.01)

    truck13 = Transport(name='truck13', resources={com1_loc1_out}, trans_max=truck_cap13,
                        label='Truck from location 1 to 3', capex=0.3 / scale_factor, vopex=0.03, trans_min=0.01,
                        varying=[VaryingTransport.DETERMINISTIC_CAPACITY])
    # truck31 = Transport(name='truck31', resources={com1_loc3_out}, trans_max=truck_cap13,
    #                     label='Truck from location 3 to 1', capex=0.0001, vopex=0.03, trans_min=0.01)

    truck24 = Transport(name='truck24', resources={com1_loc2_out}, trans_max=truck_cap24,
                        label='Truck from location 2 to 4', capex=0.5 / scale_factor, vopex=0.05, trans_min=0.01,
                        varying=[VaryingTransport.DETERMINISTIC_CAPACITY])
    # truck42 = Transport(name='truck42', resources={com1_loc4_out}, trans_max=truck_cap24,
    #                     label='Truck from location 4 to 2', capex=0.0001, vopex=0.05, trans_min=0.01)

    truck25 = Transport(name='truck25', resources={com1_loc2_out}, trans_max=truck_cap25,
                        label='Truck from location 2 to 5', capex=0.3 / scale_factor, vopex=0.03, trans_min=0.01,
                        varying=[VaryingTransport.DETERMINISTIC_CAPACITY])
    # truck52 = Transport(name='truck52', resources={com1_loc5_out}, trans_max=truck_cap25,
    #                     label='Truck from location 5 to 2', capex=0.0001, vopex=0.03, trans_min=0.01)

    truck34 = Transport(name='truck34', resources={com1_loc3_out}, trans_max=truck_cap34,
                        label='Truck from location 3 to 4', capex=0.2 / scale_factor, vopex=0.02, trans_min=0.01,
                        varying=[VaryingTransport.DETERMINISTIC_CAPACITY])
    # truck43 = Transport(name='truck43', resources={com1_loc4_out}, trans_max=truck_cap34,
    #                     label='Truck from location 4 to 3', capex=0.0001, vopex=0.02, trans_min=0.01)

    truck45 = Transport(name='truck45', resources={com1_loc4_out}, trans_max=truck_cap45,
                        label='Truck from location 4 to 5', capex=1 / scale_factor, vopex=0.1, trans_min=0.01,
                        varying=[VaryingTransport.DETERMINISTIC_CAPACITY])
    # truck54 = Transport(name='truck54', resources={com1_loc5_out}, trans_max=truck_cap45,
    #                     label='Truck from location 5 to 4', capex=0.0001, vopex=0.1, trans_min=0.01)

    truck47 = Transport(name='truck47', resources={com1_loc4_out}, trans_max=truck_cap47,
                        label='Truck from location 4 to 7', capex=0.4 / scale_factor, vopex=0.04, trans_min=0.01,
                        varying=[VaryingTransport.DETERMINISTIC_CAPACITY])
    # truck74 = Transport(name='truck74', resources={com1_loc7_out}, trans_max=truck_cap47,
    #                     label='Truck from location 7 to 4', capex=0.0001, vopex=0.04, trans_min=0.01)

    truck64 = Transport(name='truck64', resources={com1_loc6_out}, trans_max=truck_cap64,
                        label='Truck from location 6 to 4', capex=0.5 / scale_factor, vopex=0.05, trans_min=0.01,
                        varying=[VaryingTransport.DETERMINISTIC_CAPACITY])
    # truck46 = Transport(name='truck46', resources={com1_loc4_out}, trans_max=truck_cap64,
    #                     label='Truck from location 4 to 6', capex=0.0001, vopex=0.05, trans_min=0.01)

    truck75 = Transport(name='truck75', resources={com1_loc7_out}, trans_max=truck_cap75,
                        label='Truck from location 7 to 5', capex=0.4 / scale_factor, vopex=0.04, trans_min=0.01,
                        varying=[VaryingTransport.DETERMINISTIC_CAPACITY])
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
                      transport_matrix=transport_matrix, distance_matrix=distance_matrix,
                      transport_capacity_scale_level=1,
                      transport_capacity_factor={(loc1, loc2): {truck12: scen_df[[('trans12', 'com1_loc1_out')]] if (
                                                                                                                    'trans12',
                                                                                                                    'com1_loc1_out') in scen_df else default_df},
                                                 (loc1, loc3): {truck13: scen_df[[('trans13', 'com1_loc1_out')]] if (
                                                                                                                    'trans13',
                                                                                                                    'com1_loc1_out') in scen_df else default_df},
                                                 (loc2, loc4): {truck24: scen_df[[('trans24', 'com1_loc2_out')]] if (
                                                                                                                    'trans24',
                                                                                                                    'com1_loc2_out') in scen_df else default_df},
                                                 (loc2, loc5): {truck25: scen_df[[('trans25', 'com1_loc2_out')]] if (
                                                                                                                    'trans25',
                                                                                                                    'com1_loc2_out') in scen_df else default_df},
                                                 (loc3, loc4): {truck34: scen_df[[('trans34', 'com1_loc3_out')]] if (
                                                                                                                    'trans34',
                                                                                                                    'com1_loc3_out') in scen_df else default_df},
                                                 (loc4, loc5): {truck45: scen_df[[('trans45', 'com1_loc4_out')]] if (
                                                                                                                    'trans45',
                                                                                                                    'com1_loc4_out') in scen_df else default_df},
                                                 (loc4, loc7): {truck47: scen_df[[('trans47', 'com1_loc4_out')]] if (
                                                                                                                    'trans47',
                                                                                                                    'com1_loc4_out') in scen_df else default_df},
                                                 (loc6, loc4): {truck64: scen_df[[('trans64', 'com1_loc6_out')]] if (
                                                                                                                    'trans64',
                                                                                                                    'com1_loc6_out') in scen_df else default_df},
                                                 (loc7, loc5): {truck75: scen_df[[('trans75', 'com1_loc7_out')]] if (
                                                                                                                    'trans75',
                                                                                                                    'com1_loc7_out') in scen_df else default_df},
                                                 })

    # ======================================================================================================================
    # Declare scenario
    # ======================================================================================================================

    daily_demand = 400 * scale_factor
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
        # capex_process = sum(problem_mincost.Capex_network[scale_] for scale_ in scale_iter)
        # cost_trans_capex = sum(problem_mincost.Capex_transport_network[scale_] for scale_ in scale_iter)

        problem_mincost.first_stage_cost = Var(within=NonNegativeReals, doc='First Stage Cost')

        def first_stage_cost_rule(instance):
            return (instance.first_stage_cost == sum(instance.Capex_network[scale_] for scale_ in scale_iter) +
                    sum(instance.Capex_transport_network[scale_] for scale_ in scale_iter))

        problem_mincost.constraint_first_stage_cost = Constraint(rule=first_stage_cost_rule)

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
    # capex_process = sum(problem_mincost.Capex_network[scale_] for scale_ in scale_iter)
    # cost_trans_capex = sum(problem_mincost.Capex_transport_network[scale_] for scale_ in scale_iter)

    problem_mincost.first_stage_cost = Var(within=NonNegativeReals, doc='First Stage Cost')

    def first_stage_cost_rule(instance):
        return (instance.first_stage_cost == sum(instance.Capex_network[scale_] for scale_ in scale_iter) +
                sum(instance.Capex_transport_network[scale_] for scale_ in scale_iter))

    problem_mincost.constraint_first_stage_cost = Constraint(rule=first_stage_cost_rule)

    return scenario, problem_mincost

def scenario_creator(scen_name, **kwargs):
    scen_dict = kwargs.get('scenario_dict')
    scen, model = build_smodel(scen_df=scen_dict[scen_name]['factor'])
    sputils.attach_root_node(model, model.first_stage_cost,
                             [model.X_P, model.Cap_P, model.X_S, model.Cap_S, model.X_F, model.Cap_F])
    model._mpisppy_probability = scen_dict[scen_name]['prob']
    return model


def fix_variables(model1: ConcreteModel, model2: ConcreteModel, scen_name: str):
    # vars_to_fix = ['X_P', 'Cap_P', 'X_S', 'Cap_S', 'X_F', 'Cap_F']
    model = getattr(model1, scen_name)

    def fix(var1, var2):
        for i in list(var1.keys()):
            if var1[i].value is None:
                continue
            else:
                var2[i].fixed = True
                var2[i] = var1[i].value
            # var2[i].pprint()

    fix(model.X_P, model2.X_P)
    fix(model.Cap_P, model2.Cap_P)
    fix(model.X_S, model2.X_S)
    fix(model.Cap_S, model2.Cap_S)
    fix(model.X_F, model2.X_F)
    fix(model.Cap_F, model2.Cap_F)

if __name__ == '__main__':
    solver_options = {
        'MIPGap': 0.005,
        # 'TimeLimit': 60 * 15,
        'Heuristics': 0.20
    }
    
    hprc_folder = r'/scratch/user/shivam.vedant/Scripts/TSSP/AIChE2024/min_p'
    FD_folder = r'FD_LP_pkl'

    with open(fr'{hprc_folder}/scenario_dict_LP.pkl', 'rb') as file:
    # with open(r'scenario_dict_HP.pkl', 'rb') as file:
        load_scenario_dict = pickle.load(file)
    load_scenario_names = list(load_scenario_dict.keys())

    with open(fr'{hprc_folder}/sorted_result_4096_LP.pkl', 'rb') as file:
    # with open(r'sorted_result_4096_HP.pkl', 'rb') as file:
        load_sorted_result = pickle.load(file)

    scenarios_to_select = 400
    # random.seed(2)
    selected_scenarios = pick_scenarios(sorted_dict=load_sorted_result, n=scenarios_to_select, scenario_dict=load_scenario_dict)

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

    # print(selected_scenario_names)

    prob_select = sum_probabilities(selected_scenario_dict)
    print(f'Sum of probabilities of selected scenarios: {prob_select:.6f}')

    start_time = time.time()
    options = {"solver": "gurobi"}
    scenario_creator_kwargs = {'scenario_dict': selected_scenario_dict}
    ef_UI = ExtensiveForm(options, selected_scenario_names, scenario_creator,
                          scenario_creator_kwargs=scenario_creator_kwargs)
    results = ef_UI.solve_extensive_form(solver_options=solver_options)
    end_time = time.time()

    exCost_UI = ef_UI.get_objective_value()
    ssoln_UI = ef_UI.get_root_solution()

    with open(fr"{hprc_folder}/results/ssoln_{len(selected_scenario_names)}_UI_LP.pkl",'wb') as file:
        pickle.dump(ssoln_UI, file)

    exCost_FD = 0
    exPen_FD = 0
    results_FD = dict()
    scen_FD, model_FD = build_model()

    # Deterministic Scenarios for Fixed Design
    counter = 0
    FD_output_dict = dict()
    fix_variables(model1=ef_UI.ef, model2=model_FD, scen_name=selected_scenario_names[0])

    for scen_name in load_scenario_names:
        scen_FD = build_model(scen_df=load_scenario_dict[scen_name]['factor'])
        counter += 1
        # Delete process capacity factors, resource availability factors, transport capacity factors
        model_FD.del_component('constraint_nameplate_production_varying_capacity')
        model_FD.del_component('constraint_resource_consumption_varying')
        model_FD.del_component('constraint_export')

        # Add the constraints back for this particular scenario
        model_FD.constraint_nameplate_production_varying_capacity = make_constraint(instance=model_FD,
                                                                                    type_cons=Cons.X_LEQ_BY,
                                                                                    variable_x='P',
                                                                                    location_set=model_FD.locations,
                                                                                    component_set=model_FD.processes_varying_capacity,
                                                                                    loc_comp_dict=scen_FD.location_process_dict,
                                                                                    b_factor=scen_FD.capacity_factor,
                                                                                    x_scale_level=scen_FD.scheduling_scale_level,
                                                                                    b_scale_level=scen_FD.capacity_scale_level,
                                                                                    y_scale_level=scen_FD.network_scale_level,
                                                                                    variable_y='Cap_P',
                                                                                    label='restricts production to varying nameplate capacity')

        model_FD.constraint_resource_consumption_varying = make_constraint(
            instance=model_FD, type_cons=Cons.X_LEQ_B, variable_x='C', location_set=model_FD.locations,
            component_set=model_FD.resources_varying_availability, b_max=scen_FD.cons_max,
            loc_comp_dict=scen_FD.location_resource_dict, b_factor=scen_FD.availability_factor,
            x_scale_level=scen_FD.scheduling_scale_level, b_scale_level=scen_FD.availability_scale_level,
            label='restricts resource consumption to varying availablity')

        constraint_export(instance=model_FD, scheduling_scale_level=scen_FD.scheduling_scale_level,
                          network_scale_level=scen_FD.network_scale_level,
                          location_transport_resource_dict=scen_FD.location_transport_resource_dict,
                          transport_capacity_factor=scen_FD.transport_capacity_factor,
                          transport_capacity_scale_level=scen_FD.transport_capacity_scale_level)

        results_FD = solve(scenario=scen_FD, instance=model_FD, solver='gurobi', name=scen_name,
                           solver_options=solver_options)

        print(
            f'######################## Finished solving {scen_name} ({counter} of {len(load_scenario_dict)}) ########################')

        model_vars = model_FD.component_map(ctype=Var)
        vars_dict = {i: model_vars[i].extract_values() for i in model_vars.keys()}
        obj_dict = {'objective': pyoval(model_FD.objective_cost_w_demand_penalty)}

        FD_output_dict[scen_name] = {**vars_dict, **obj_dict}

        with open(f"{scen_name}.pkl", 'wb') as file:
            pickle.dump(FD_output_dict[scen_name], file)

        exCost_FD += pyoval(model_FD.objective_cost_w_demand_penalty) * load_scenario_dict[scen_name]['prob']
        exPen_FD += pyoval(model_FD.Demand_penalty_network[('com1_sold', 0)]) * load_scenario_dict[scen_name]['prob']

    exRes_UI = 1 - exPen_FD / (20 * 400 * 90 * 4)

    m = getattr(ef_UI.ef, selected_scenario_names[0])
    fsc = pyoval(m.first_stage_cost)

    print(f'Total Expected Cost considering disruptions: {exCost_UI:.4f}')
    print(f'Total Expected Demand Fulfillment considering disruptions: {exRes_UI:.4f}')
    print(f'First Stage Cost: {fsc:.4f}')
    print(f'Execution time: {start_time - end_time:.4f} seconds')

    final_results_dict = {len(selected_scenario_names): {'Expected Cost UI': exCost_UI,
                                                         'Expected Cost FD': exCost_FD,
                                                         'Expected Resilience': exRes_UI,
                                                         'First Stage Cost': fsc,
                                                         'Execution Time': end_time - start_time}}

    with open(fr"{hprc_folder}/results/FD_{len(selected_scenario_names)}_final_results_LP.pkl", 'wb') as file:
        pickle.dump(final_results_dict, file)
