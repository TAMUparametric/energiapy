from pyomo.environ import *
from pyomo.environ import Binary, NonNegativeReals, value, Var
import matplotlib.pyplot as plt
from matplotlib import rc
import sys
sys.path.append('../../../../src')
# sys.path.append('/scratch/user/shivam.vedant')
import mpisppy.utils.sputils as sputils
import pandas
from energiapy.components.temporal_scale import TemporalScale
from energiapy.components.resource import Resource, VaryingResource
from energiapy.components.process import Process, ProcessMode, VaryingProcess
from energiapy.components.location import Location
from energiapy.components.transport import Transport
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
import pickle

def create_list(n:int):
    n_dict = {1: 13, 2: 26, 3: 39, 4: 52}
    return [1]*n_dict[n] + [0]*(_exec_scenarios - n_dict[n])

def build_model(scen_name):
    default_df = pandas.DataFrame(data=[1] * _exec_scenarios)

    # Define temporal scales
    scales = TemporalScale(discretization_list=[1, _exec_scenarios, _time_intervals])

    # ======================================================================================================================
    # Declare resources/commodities
    # ======================================================================================================================
    com1_pur = Resource(name='com1_pur', cons_max=M, block={'imp': 1, 'urg': 1}, price=0.00,
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
    com1_process_capacity = 250

    # prod_max = {0: 0.25*com1_process_capacity, 1: 0.5*com1_process_capacity, 2: 0.75*com1_process_capacity, 3: 0.95*com1_process_capacity, 4: com1_process_capacity}
    # prod_min = {0: 0, 1: 0.25*com1_process_capacity, 2: 0.5*com1_process_capacity, 3: 0.75*com1_process_capacity, 4: 0.95*com1_process_capacity}
    # rate_max = {0:1.25/2, 1: 1/2, 2: 0.75/2, 3: 0.5/2, 4: 0.25/2}
    # mode_ramp = {(0,1): 5, (1,2): 5}

    com1_procure = Process(name='procure com1', prod_max=150, conversion={com1_pur: -1, com1_in: 1},
                           capex=0.1, vopex=0.01, prod_min=0.01, label='Procure com1')
    com1_sell = Process(name='sell com1', prod_max=150, conversion={com1_out: -1, com1_sold: 1},
                        capex=0.1, vopex=0.01, prod_min=0.01, label='Sell com1')
    # com1_opt_procure = Process(name='procure optional com1', prod_max=75, conversion={com1_pur: -1, com1_in:1}, capex=10, vopex=0.1, prod_min=0.01, label='Procure optional com1')

    com1_receive_loc1 = Process(name='com1_receive_loc1', prod_max=com1_process_capacity,
                                conversion={com1_loc1_out: -1, com1_in: 1}, capex=0.1, vopex=0.01, prod_min=0.01,
                                label='Commodity 1 received from location 1')
    com1_receive_loc2 = Process(name='com1_receive_loc2', prod_max=com1_process_capacity,
                                conversion={com1_loc2_out: -1, com1_in: 1}, capex=0.1, vopex=0.01, prod_min=0.01,
                                label='Commodity 1 received from location 2')
    com1_receive_loc3 = Process(name='com1_receive_loc3', prod_max=com1_process_capacity,
                                conversion={com1_loc3_out: -1, com1_in: 1}, capex=0.1, vopex=0.01, prod_min=0.01,
                                label='Commodity 1 received from location 3')
    com1_receive_loc4 = Process(name='com1_receive_loc4', prod_max=com1_process_capacity,
                                conversion={com1_loc4_out: -1, com1_in: 1}, capex=0.1, vopex=0.01, prod_min=0.01,
                                label='Commodity 1 received from location 4')
    com1_receive_loc5 = Process(name='com1_receive_loc5', prod_max=com1_process_capacity,
                                conversion={com1_loc5_out: -1, com1_in: 1}, capex=0.1, vopex=0.01, prod_min=0.01,
                                label='Commodity 1 received from location 5')
    com1_receive_loc6 = Process(name='com1_receive_loc6', prod_max=com1_process_capacity,
                                conversion={com1_loc6_out: -1, com1_in: 1}, capex=0.1, vopex=0.01, prod_min=0.01,
                                label='Commodity 1 received from location 6')
    com1_receive_loc7 = Process(name='com1_receive_loc7', prod_max=com1_process_capacity,
                                conversion={com1_loc7_out: -1, com1_in: 1}, capex=0.1, vopex=0.01, prod_min=0.01,
                                label='Commodity 1 received from location 7')

    com1_process = Process(name='com1_process', prod_max=com1_process_capacity, conversion={com1_in: -1, com1_out: 1},
                           capex=0.1, vopex=0.01, prod_min=0.01, label='Process the commodity through the location',
                           varying=[VaryingProcess.DETERMINISTIC_CAPACITY])

    # com1_process = Process(name='com1_process', prod_max=prod_max, conversion={0:{com1_in: -1, com1_out: 1}, 1:{com1_in: -1, com1_out: 1}, 2:{com1_in: -1, com1_out: 1}, 3:{com1_in: -1, com1_out: 1}, 4:{com1_in: -1, com1_out: 1}},  capex=0.01, vopex=0.01, prod_min=prod_min, rate_max=rate_max, varying=[VaryingProcess.DETERMINISTIC_CAPACITY], label='Process the commodity through the location')

    #com1_store10 = Process(name='com1_store10', prod_max=com1_process_capacity, capex=0.1, vopex=0.01, storage_capex=10,
    #                       store_min=0.01, store_max=40, prod_min=0.01, label="Storage capacity of 10 units",
    #                       storage=com1_in, storage_cost=0.02)
    #com1_store20 = Process(name='com1_store20', prod_max=com1_process_capacity, capex=0.1, vopex=0.02, storage_capex=20,
    #                       store_min=0.01, store_max=80, prod_min=0.01, label="Storage capacity of 20 units",
    #                       storage=com1_in, storage_cost=0.02)
    #com1_store50 = Process(name='com1_store50', prod_max=com1_process_capacity, capex=0.1, vopex=0.05, storage_capex=50,
    #                       store_min=0.01, store_max=200, prod_min=0.01, label="Storage capacity of 50 units",
    #                       storage=com1_in, storage_cost=0.02)

    com1_store = Process(name='com1_store', prod_max=com1_process_capacity, capex=0.1, vopex=0.01, storage_capex=30, store_min=0.01, store_max=200, prod_min=0.01, label="Storage process", storage=com1_in, storage_cost=0.02)

    com1_loc1_send = Process(name='com1_loc1_send', prod_max=com1_process_capacity,
                             conversion={com1_out: -1, com1_loc1_out: 1}, capex=0.1, vopex=0.01, prod_min=0.01,
                             label='Send commodity one from location 1')
    com1_loc2_send = Process(name='com1_loc2_send', prod_max=com1_process_capacity,
                             conversion={com1_out: -1, com1_loc2_out: 1}, capex=0.1, vopex=0.01, prod_min=0.01,
                             label='Send commodity one from location 2')
    com1_loc3_send = Process(name='com1_loc3_send', prod_max=com1_process_capacity,
                             conversion={com1_out: -1, com1_loc3_out: 1}, capex=0.1, vopex=0.01, prod_min=0.01,
                             label='Send commodity one from location 3')
    com1_loc4_send = Process(name='com1_loc4_send', prod_max=com1_process_capacity,
                             conversion={com1_out: -1, com1_loc4_out: 1}, capex=0.1, vopex=0.01, prod_min=0.01,
                             label='Send commodity one from location 4')
    com1_loc5_send = Process(name='com1_loc5_send', prod_max=com1_process_capacity,
                             conversion={com1_out: -1, com1_loc5_out: 1}, capex=0.1, vopex=0.01, prod_min=0.01,
                             label='Send commodity one from location 5')
    com1_loc6_send = Process(name='com1_loc6_send', prod_max=com1_process_capacity,
                             conversion={com1_out: -1, com1_loc6_out: 1}, capex=0.1, vopex=0.01, prod_min=0.01,
                             label='Send commodity one from location 6')
    com1_loc7_send = Process(name='com1_loc7_send', prod_max=com1_process_capacity,
                             conversion={com1_out: -1, com1_loc7_out: 1}, capex=0.1, vopex=0.01, prod_min=0.01,
                             label='Send commodity one from location 7')

    # ======================================================================================================================
    # Declare locations/warehouses
    # ======================================================================================================================
    loc1 = Location(name='loc1',
                    processes={com1_procure, com1_receive_loc2, com1_receive_loc3, com1_process, com1_store, com1_loc1_send}, label="Location 1",
                    scales=scales, demand_scale_level=2, capacity_scale_level=1, availability_scale_level=1,
                    availability_factor={com1_pur: scenario_dictionary[scen_name]['factor'][[('loc1', 'com1_pur')]] if (
                                                                                                                       'loc1',
                                                                                                                       'com1_pur') in
                                                                                                                       scenario_dictionary[
                                                                                                                           scen_name][
                                                                                                                           'factor'] else default_df})

    loc2 = Location(name='loc2',
                    processes={com1_receive_loc1, com1_receive_loc4, com1_receive_loc5, com1_process, com1_store, com1_loc2_send}, label="Location 2", scales=scales,
                    demand_scale_level=2, capacity_scale_level=1, availability_scale_level=1,
                    capacity_factor={
                        com1_process: scenario_dictionary[scen_name]['factor'][[('loc2', 'com1_process')]] if ('loc2',
                                                                                                               'com1_process') in
                                                                                                              scenario_dictionary[
                                                                                                                  scen_name][
                                                                                                                  'factor'] else default_df})

    loc3 = Location(name='loc3',
                    processes={com1_receive_loc1, com1_receive_loc4, com1_process, com1_store, com1_loc3_send}, label="Location 3", scales=scales, demand_scale_level=2,
                    capacity_scale_level=1, availability_scale_level=1)

    loc4 = Location(name='loc4', processes={com1_receive_loc2, com1_receive_loc3, com1_receive_loc6, com1_receive_loc5,
                                            com1_receive_loc7, com1_process, com1_store,
                                            com1_loc4_send}, label="Location 4", scales=scales, demand_scale_level=2,
                    capacity_scale_level=1, availability_scale_level=1,
                    capacity_factor={
                        com1_process: scenario_dictionary[scen_name]['factor'][[('loc4', 'com1_process')]] if ('loc4',
                                                                                                               'com1_process') in
                                                                                                              scenario_dictionary[
                                                                                                                  scen_name][
                                                                                                                  'factor'] else default_df})

    loc5 = Location(name='loc5',
                    processes={com1_receive_loc2, com1_receive_loc4, com1_receive_loc7, com1_process, com1_store, com1_loc5_send, com1_sell}, label="Location 5",
                    scales=scales, demand_scale_level=2, capacity_scale_level=1, availability_scale_level=1)

    loc6 = Location(name='loc6',
                    processes={com1_procure, com1_receive_loc4, com1_process, com1_store,
                               com1_loc6_send}, label="Location 6", scales=scales, demand_scale_level=2,
                    capacity_scale_level=1, availability_scale_level=1,
                    availability_factor={com1_pur: scenario_dictionary[scen_name]['factor'][[('loc6', 'com1_pur')]] if (
                                                                                                                       'loc6',
                                                                                                                       'com1_pur') in
                                                                                                                       scenario_dictionary[
                                                                                                                           scen_name][
                                                                                                                           'factor'] else default_df},
                    capacity_factor={
                        com1_process: scenario_dictionary[scen_name]['factor'][[('loc6', 'com1_process')]] if ('loc6',
                                                                                                               'com1_process') in
                                                                                                              scenario_dictionary[
                                                                                                                  scen_name][
                                                                                                                  'factor'] else default_df})

    loc7 = Location(name='loc7',
                    processes={com1_receive_loc4, com1_receive_loc5, com1_process, com1_store, com1_loc7_send}, label="Location 7", scales=scales, demand_scale_level=2,
                    capacity_scale_level=1, availability_scale_level=1,
                    capacity_factor={
                        com1_process: scenario_dictionary[scen_name]['factor'][[('loc7', 'com1_process')]] if ('loc7',
                                                                                                               'com1_process') in
                                                                                                              scenario_dictionary[
                                                                                                                  scen_name][
                                                                                                                  'factor'] else default_df})

    # ======================================================================================================================
    # Declare transport/trucks
    # ======================================================================================================================

    truck_cap12 = 70
    truck_cap13 = 30
    truck_cap24 = 50
    truck_cap25 = 30
    truck_cap34 = 30
    truck_cap45 = 100
    truck_cap47 = 40
    truck_cap64 = 50
    truck_cap75 = 40

    truck12 = Transport(name='truck12', resources={com1_loc1_out}, trans_max=truck_cap12,
                        label='Truck from location 1 to 2', capex=0.5, vopex=0.05, trans_min=truck_cap12)
    truck21 = Transport(name='truck21', resources={com1_loc2_out}, trans_max=truck_cap12,
                        label='Truck from location 2 to 1', capex=0.0001, vopex=0.05, trans_min=truck_cap12)

    truck13 = Transport(name='truck13', resources={com1_loc1_out}, trans_max=truck_cap13,
                        label='Truck from location 1 to 3', capex=0.3, vopex=0.03, trans_min=truck_cap13)
    truck31 = Transport(name='truck31', resources={com1_loc3_out}, trans_max=truck_cap13,
                        label='Truck from location 3 to 1', capex=0.0001, vopex=0.03, trans_min=truck_cap13)

    truck24 = Transport(name='truck24', resources={com1_loc2_out}, trans_max=truck_cap24,
                        label='Truck from location 2 to 4', capex=0.5, vopex=0.05, trans_min=truck_cap24)
    truck42 = Transport(name='truck42', resources={com1_loc4_out}, trans_max=truck_cap24,
                        label='Truck from location 4 to 2', capex=0.0001, vopex=0.05, trans_min=truck_cap24)

    truck25 = Transport(name='truck25', resources={com1_loc2_out}, trans_max=truck_cap25,
                        label='Truck from location 2 to 5', capex=0.3, vopex=0.03, trans_min=truck_cap25)
    truck52 = Transport(name='truck52', resources={com1_loc5_out}, trans_max=truck_cap25,
                        label='Truck from location 5 to 2', capex=0.0001, vopex=0.03, trans_min=truck_cap25)

    truck34 = Transport(name='truck34', resources={com1_loc3_out}, trans_max=truck_cap34,
                        label='Truck from location 3 to 4', capex=0.2, vopex=0.02, trans_min=truck_cap34)
    truck43 = Transport(name='truck43', resources={com1_loc4_out}, trans_max=truck_cap34,
                        label='Truck from location 4 to 3', capex=0.0001, vopex=0.02, trans_min=truck_cap34)

    truck45 = Transport(name='truck45', resources={com1_loc4_out}, trans_max=truck_cap45,
                        label='Truck from location 4 to 5', capex=1, vopex=0.1, trans_min=truck_cap45)
    truck54 = Transport(name='truck54', resources={com1_loc5_out}, trans_max=truck_cap45,
                        label='Truck from location 5 to 4', capex=0.0001, vopex=0.1, trans_min=truck_cap45)

    truck47 = Transport(name='truck47', resources={com1_loc4_out}, trans_max=truck_cap47,
                        label='Truck from location 4 to 7', capex=0.4, vopex=0.04, trans_min=truck_cap47)
    truck74 = Transport(name='truck74', resources={com1_loc7_out}, trans_max=truck_cap47,
                        label='Truck from location 7 to 4', capex=0.0001, vopex=0.04, trans_min=truck_cap47)

    truck64 = Transport(name='truck64', resources={com1_loc6_out}, trans_max=truck_cap64,
                        label='Truck from location 6 to 4', capex=0.5, vopex=0.05, trans_min=truck_cap64)
    truck46 = Transport(name='truck46', resources={com1_loc4_out}, trans_max=truck_cap64,
                        label='Truck from location 4 to 6', capex=0.0001, vopex=0.05, trans_min=truck_cap64)

    truck75 = Transport(name='truck75', resources={com1_loc7_out}, trans_max=truck_cap75,
                        label='Truck from location 7 to 5', capex=0.4, vopex=0.04, trans_min=truck_cap75)
    truck57 = Transport(name='truck57', resources={com1_loc5_out}, trans_max=truck_cap75,
                        label='Truck from location 5 to 7', capex=0.0001, vopex=0.04, trans_min=truck_cap75)

    # ======================================================================================================================
    # Declare network
    # ======================================================================================================================

    transport_matrix = [
        [[], [truck12], [truck13], [], [], [], []],  # source: location 1
        [[truck21], [], [], [truck24], [truck25], [], []],  # source: location 2
        [[truck31], [], [], [truck34], [], [], []],  # source: location 3
        [[], [truck42], [truck43], [], [truck45], [truck46], [truck47]],  # source: location 4
        [[], [truck52], [], [truck54], [], [], [truck57]],  # source: location 5
        [[], [], [], [truck64], [], [], []],  # source: location 6
        [[], [], [], [truck74], [truck75], [], []]  # source: location 7
    ]

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
                      transport_matrix=transport_matrix, distance_matrix=distance_matrix)

    # ======================================================================================================================
    # Declare scenario
    # ======================================================================================================================

    daily_demand = 100
    demand_penalty = 20

    demand_dict = {i: {com1_sold: daily_demand} if i == loc5 else {com1_sold: 0} for i in locset}
    demand_penalty_dict = {i: {com1_sold: demand_penalty} if i == loc5 else {com1_sold: 0} for i in locset}

    scenario = Scenario(name='scenario', scales=scales, scheduling_scale_level=2, network_scale_level=0,
                        purchase_scale_level=2, availability_scale_level=1, demand_scale_level=2,
                        capacity_scale_level=1, network=network, demand=demand_dict, demand_penalty=demand_penalty_dict,
                        label='Stochastic scenario with Multiple Locations')

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

if __name__ == '__main__':
    _time_intervals = 7  # Number of time intervals in a planning horizon    (L_chi)
    _coms = 1
    _exec_scenarios = 52  # Number of execution scenarios                     (chi)

    M = 1e3  # Big M

    scenario_dictionary = {
        # 'cap1_1': {'prob': 0.2, 'factor': pandas.DataFrame(data={('loc1','com1_process'): create_list(1)})},
        # 'cap1_2': {'prob': 0.4, 'factor': pandas.DataFrame(data={('loc1', 'com1_process'): create_list(2)})},
        # 'cap1_3': {'prob': 0.2, 'factor': pandas.DataFrame(data={('loc1', 'com1_process'): create_list(3)})},
        # 'cap1_4': {'prob': 0.2, 'factor': pandas.DataFrame(data={('loc1', 'com1_process'): create_list(4)})},
        #
        'cap2_1': {'prob': 0.2, 'factor': pandas.DataFrame(data={('loc2', 'com1_process'): create_list(1)})},
        'cap2_2': {'prob': 0.4, 'factor': pandas.DataFrame(data={('loc2', 'com1_process'): create_list(2)})},
        'cap2_3': {'prob': 0.2, 'factor': pandas.DataFrame(data={('loc2', 'com1_process'): create_list(3)})},
        'cap2_4': {'prob': 0.2, 'factor': pandas.DataFrame(data={('loc2', 'com1_process'): create_list(4)})},
        #
        # 'cap3_1': {'prob': 0.25, 'factor': pandas.DataFrame(data={('loc3','com1_process'): create_list(1)})},
        # 'cap3_2': {'prob': 0.25, 'factor': pandas.DataFrame(data={('loc3', 'com1_process'): create_list(2)})},
        # 'cap3_3': {'prob': 0.25, 'factor': pandas.DataFrame(data={('loc3', 'com1_process'): create_list(3)})},
        # 'cap3_4': {'prob': 0.25, 'factor': pandas.DataFrame(data={('loc3', 'com1_process'): create_list(4)})},
        #
        'cap4_1': {'prob': 0.1, 'factor': pandas.DataFrame(data={('loc4', 'com1_process'): create_list(1)})},
        'cap4_2': {'prob': 0.2, 'factor': pandas.DataFrame(data={('loc4', 'com1_process'): create_list(2)})},
        'cap4_3': {'prob': 0.3, 'factor': pandas.DataFrame(data={('loc4', 'com1_process'): create_list(3)})},
        'cap4_4': {'prob': 0.4, 'factor': pandas.DataFrame(data={('loc4', 'com1_process'): create_list(4)})},
        #
        # 'cap5_1': {'prob': 0.25, 'factor': pandas.DataFrame(data={('loc5','com1_process'): create_list(1)})},
        # 'cap5_2': {'prob': 0.25, 'factor': pandas.DataFrame(data={('loc5', 'com1_process'): create_list(2)})},
        # 'cap5_3': {'prob': 0.25, 'factor': pandas.DataFrame(data={('loc5', 'com1_process'): create_list(3)})},
        # 'cap5_4': {'prob': 0.25, 'factor': pandas.DataFrame(data={('loc5', 'com1_process'): create_list(4)})},
        #
        #'cap6_1': {'prob': 0.1, 'factor': pandas.DataFrame(data={('loc6', 'com1_process'): create_list(1)})},
        #'cap6_2': {'prob': 0.1, 'factor': pandas.DataFrame(data={('loc6', 'com1_process'): create_list(2)})},
        #'cap6_3': {'prob': 0.5, 'factor': pandas.DataFrame(data={('loc6', 'com1_process'): create_list(3)})},
        #'cap6_4': {'prob': 0.3, 'factor': pandas.DataFrame(data={('loc6', 'com1_process'): create_list(4)})},

        'cap7_1': {'prob': 0.15, 'factor': pandas.DataFrame(data={('loc7', 'com1_process'): create_list(1)})},
        'cap7_2': {'prob': 0.2, 'factor': pandas.DataFrame(data={('loc7', 'com1_process'): create_list(2)})},
        'cap7_3': {'prob': 0.25, 'factor': pandas.DataFrame(data={('loc7', 'com1_process'): create_list(3)})},
        'cap7_4': {'prob': 0.4, 'factor': pandas.DataFrame(data={('loc7', 'com1_process'): create_list(4)})},
        #
        'res1_1': {'prob': 0.25, 'factor': pandas.DataFrame(data={('loc1', 'com1_pur'): create_list(1)})},
        'res1_2': {'prob': 0.3, 'factor': pandas.DataFrame(data={('loc1', 'com1_pur'): create_list(2)})},
        'res1_3': {'prob': 0.15, 'factor': pandas.DataFrame(data={('loc1', 'com1_pur'): create_list(3)})},
        'res1_4': {'prob': 0.3, 'factor': pandas.DataFrame(data={('loc1', 'com1_pur'): create_list(4)})},

        'res6_1': {'prob': 0.1, 'factor': pandas.DataFrame(data={('loc6', 'com1_pur'): create_list(1)})},
        'res6_2': {'prob': 0.25, 'factor': pandas.DataFrame(data={('loc6', 'com1_pur'): create_list(2)})},
        'res6_3': {'prob': 0.2, 'factor': pandas.DataFrame(data={('loc6', 'com1_pur'): create_list(3)})},
        'res6_4': {'prob': 0.45, 'factor': pandas.DataFrame(data={('loc6', 'com1_pur'): create_list(4)})},
        #
        # 'trans14_1': {'prob': 0.25, 'factor': pandas.DataFrame(data={'trans14': create_list(1)})},
        # 'trans14_2': {'prob': 0.25, 'factor': pandas.DataFrame(data={'trans14': create_list(2)})},
        # 'trans14_3': {'prob': 0.25, 'factor': pandas.DataFrame(data={'trans14': create_list(3)})},
        # 'trans14_4': {'prob': 0.25, 'factor': pandas.DataFrame(data={'trans14': create_list(4)})},
    }

    scenario_names = list(scenario_dictionary.keys())

    total_prob = sum(scenario_dictionary[name]['prob'] for name in scenario_names)

    for name in scenario_names:
        scenario_dictionary[name]['prob'] = scenario_dictionary[name]['prob'] / total_prob

    solver_options = {
        'MIPGap': 0.005,
        # 'TimeLimit': 60 * 15,
        'Heuristics': 0.20
    }

    exCost_PI = 0
    results_PI = dict()
    model_PI = dict()

    for scenario_name in scenario_names:
        scen_PI, model_PI[scenario_name] = build_model(scen_name=scenario_name)
        results_PI[scenario_name] = solve(scenario=scen_PI, instance=model_PI[scenario_name], solver='gurobi',
                                          name=scenario_name, solver_options=solver_options)

        print('######################## Finished solving ' + scenario_name + ' ########################')

        exCost_PI += value(model_PI[scenario_name].objective_cost_w_demand_penalty) * \
                     scenario_dictionary[scenario_name]['prob']


    def scenario_creator(scenario_name):
        scen, model = build_model(scen_name=scenario_name)
        sputils.attach_root_node(model, model.first_stage_cost,
                                 [model.X_P, model.Cap_P, model.X_S, model.Cap_S, model.X_F, model.Cap_F])
        model._mpisppy_probability = scenario_dictionary[scenario_name]['prob']
        return model

    options = {"solver": "gurobi"}
    # all_scenario_names = ["good", "average", "bad"]
    ef_UI = ExtensiveForm(options, scenario_names, scenario_creator)
    results = ef_UI.solve_extensive_form(solver_options=solver_options)

    UI_output_dict = dict()
    for scenario in scenario_names:
        model_vars = getattr(ef_UI.ef, scenario).component_map(ctype=Var)
        vars_dict = {i: model_vars[i].extract_values()
                     for i in model_vars.keys()}

        model_obj = getattr(ef_UI.ef, scenario).component_map(ctype=Objective)
        obj_dict = {'objective': model_obj[i]() for i in model_obj.keys()}

        UI_output_dict[scenario] = {**vars_dict, **obj_dict}

    with open('IE_MultiLoc2_stochastic.pkl', "wb") as f:
        pickle.dump(UI_output_dict, f)
        f.close()

    results_dict = pickle.load(open('IE_MultiLoc2_stochastic.pkl', "rb"))

    print(f"Expected cost under perfect information: {exCost_PI:.3f}")

    exCost_UI = ef_UI.get_objective_value()
    print(f"Expected cost under uncertainty: {exCost_UI:.3f}")

    EVPI = exCost_UI - exCost_PI
    print(f"Expected Value of Perfect Information: {EVPI:.3f}")

    #for outer_key, inner_dict in results_dict.items():
     #   print(f"{outer_key}:")
      #  print('\n'.join([f"    {k}: {v}" for k, v in inner_dict.items()]))
