import sys
sys.path.append('/scratch/user/shivam.vedant')
sys.path.append('/scratch/user/shivam.vedant/src')
# sys.path.append('../../../../../../src')

import pandas
from energiapy.components.temporal_scale import TemporalScale
from energiapy.components.resource import Resource, VaryingResource
from energiapy.components.process import Process, VaryingProcess
from energiapy.components.location import Location
from energiapy.components.transport import Transport, VaryingTransport
from energiapy.components.network import Network
from energiapy.components.scenario import Scenario
# from energiapy.model.constraints.demand import constraint_demand_lb
from energiapy.model.formulate import formulate, Constraints, Objective
from energiapy.utils.scale_utils import scale_tuple

from pyomo.environ import value as pyoval
from pyomo.environ import Var, Constraint, NonNegativeReals
# from pyomo.contrib.iis import write_iis

import time
import pickle

import mpisppy.utils.sputils as sputils
from mpisppy.opt.ef import ExtensiveForm

design_planning_horizons = 1
design_execution_scenarios = 52
design_time_intervals = 7

capacity_scale_factor = 10

M = 1e4

design_annualization_factor = 1/design_planning_horizons

def build_design_model(scen_df=pandas.DataFrame(), eps: float = 1.0):
    default_df = pandas.DataFrame(data=[1] * design_execution_scenarios)

    # Define temporal scales
    scales = TemporalScale(
        discretization_list=[design_planning_horizons, design_execution_scenarios, design_time_intervals])

    # ======================================================================================================================
    # Declare resources/commodities
    # ======================================================================================================================
    com1_pur = Resource(name='com1_pur', cons_max=500 * capacity_scale_factor,
                        block={'imp': 1, 'urg': 1}, price=0.00, label='Commodity 1 consumed from outside the system',
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
    com1_process_capacity = 500 * capacity_scale_factor
    min_process_capacity = 0.01

    com1_procure = Process(name='procure com1', prod_max=com1_process_capacity, conversion={com1_pur: -1, com1_in: 1},
                           capex=25, vopex=0.01, prod_min=min_process_capacity, label='Procure com1')
    com1_sell = Process(name='sell com1', prod_max=com1_process_capacity, conversion={com1_out: -1, com1_sold: 1},
                        capex=1, vopex=0.01, prod_min=min_process_capacity, label='Sell com1')

    com1_receive_loc1 = Process(name='com1_receive_loc1', prod_max=com1_process_capacity,
                                conversion={com1_loc1_out: -1, com1_in: 1}, capex=1,
                                vopex=0.01, prod_min=min_process_capacity, label='Commodity 1 received from location 1')
    com1_receive_loc2 = Process(name='com1_receive_loc2', prod_max=com1_process_capacity,
                                conversion={com1_loc2_out: -1, com1_in: 1}, capex=1,
                                vopex=0.01, prod_min=min_process_capacity, label='Commodity 1 received from location 2')
    com1_receive_loc3 = Process(name='com1_receive_loc3', prod_max=com1_process_capacity,
                                conversion={com1_loc3_out: -1, com1_in: 1}, capex=1,
                                vopex=0.01, prod_min=min_process_capacity, label='Commodity 1 received from location 3')
    com1_receive_loc4 = Process(name='com1_receive_loc4', prod_max=com1_process_capacity,
                                conversion={com1_loc4_out: -1, com1_in: 1}, capex=1,
                                vopex=0.01, prod_min=min_process_capacity, label='Commodity 1 received from location 4')
    # com1_receive_loc5 = Process(name='com1_receive_loc5', prod_max=com1_process_capacity,
    #                             conversion={com1_loc5_out: -1, com1_in: 1}, capex=1,
    #                             vopex=0.01, prod_min=min_process_capacity, label='Commodity 1 received from location 5')
    com1_receive_loc6 = Process(name='com1_receive_loc6', prod_max=com1_process_capacity,
                                conversion={com1_loc6_out: -1, com1_in: 1}, capex=1,
                                vopex=0.01, prod_min=min_process_capacity, label='Commodity 1 received from location 6')
    com1_receive_loc7 = Process(name='com1_receive_loc7', prod_max=com1_process_capacity,
                                conversion={com1_loc7_out: -1, com1_in: 1}, capex=1,
                                vopex=0.01, prod_min=min_process_capacity, label='Commodity 1 received from location 7')

    com1_process = Process(name='com1_process', prod_max=com1_process_capacity, conversion={com1_in: -1, com1_out: 1},
                           capex=50, vopex=0.1, prod_min=min_process_capacity,
                           varying=[VaryingProcess.DETERMINISTIC_CAPACITY],
                           label='Process the commodity through the location')

    com1_store = Process(name='com1_store', prod_max=com1_process_capacity, capex=20, vopex=5,
                         store_min=0.01, store_max=500 * capacity_scale_factor,
                         prod_min=min_process_capacity, label="Storage capacity of upto 100 units", storage=com1_in,
                         storage_cost=0.02, storage_capex=75)

    com1_loc1_send = Process(name='com1_loc1_send', prod_max=com1_process_capacity,
                             conversion={com1_out: -1, com1_loc1_out: 1}, capex=1, vopex=0.01,
                             prod_min=min_process_capacity, label='Send commodity one from location 1')
    com1_loc2_send = Process(name='com1_loc2_send', prod_max=com1_process_capacity,
                             conversion={com1_out: -1, com1_loc2_out: 1}, capex=1, vopex=0.01,
                             prod_min=min_process_capacity, label='Send commodity one from location 2')
    com1_loc3_send = Process(name='com1_loc3_send', prod_max=com1_process_capacity,
                             conversion={com1_out: -1, com1_loc3_out: 1}, capex=1, vopex=0.01,
                             prod_min=min_process_capacity, label='Send commodity one from location 3')
    com1_loc4_send = Process(name='com1_loc4_send', prod_max=com1_process_capacity,
                             conversion={com1_out: -1, com1_loc4_out: 1}, capex=1, vopex=0.01,
                             prod_min=min_process_capacity, label='Send commodity one from location 4')
    com1_loc5_send = Process(name='com1_loc5_send', prod_max=com1_process_capacity,
                             conversion={com1_out: -1, com1_loc5_out: 1}, capex=1, vopex=0.01,
                             prod_min=min_process_capacity, label='Send commodity one from location 5')
    com1_loc6_send = Process(name='com1_loc6_send', prod_max=com1_process_capacity,
                             conversion={com1_out: -1, com1_loc6_out: 1}, capex=1, vopex=0.01,
                             prod_min=min_process_capacity, label='Send commodity one from location 6')
    com1_loc7_send = Process(name='com1_loc7_send', prod_max=com1_process_capacity,
                             conversion={com1_out: -1, com1_loc7_out: 1}, capex=1, vopex=0.01,
                             prod_min=min_process_capacity, label='Send commodity one from location 7')

    # ======================================================================================================================
    # Declare locations/warehouses
    # ======================================================================================================================
    loc1 = Location(name='loc1',
                    processes={com1_procure, com1_process, com1_store, com1_loc1_send}, label="Location 1",
                    scales=scales, demand_scale_level=2, capacity_scale_level=1, availability_scale_level=1,
                    availability_factor={
                        com1_pur: scen_df[[('loc1', 'com1_pur')]] if ('loc1', 'com1_pur') in scen_df else default_df},
                    capacity_factor={com1_process: scen_df[[('loc1', 'com1_proces')]] if ('loc1',
                                                                                          'com1_proces') in scen_df else default_df})

    loc2 = Location(name='loc2', processes={com1_receive_loc1, com1_process, com1_store, com1_loc2_send},
                    label="Location 2",
                    scales=scales, demand_scale_level=2, capacity_scale_level=1, availability_scale_level=1,
                    capacity_factor={com1_process: scen_df[[('loc2', 'com1_process')]] if ('loc2',
                                                                                           'com1_process') in scen_df else default_df})

    loc3 = Location(name='loc3', processes={com1_receive_loc1, com1_process, com1_store, com1_loc3_send},
                    label="Location 3",
                    scales=scales, demand_scale_level=2, capacity_scale_level=1, availability_scale_level=1,
                    capacity_factor={com1_process: scen_df[[('loc3', 'com1_process')]] if ('loc3',
                                                                                           'com1_process') in scen_df else default_df})

    loc4 = Location(name='loc4',
                    processes={com1_receive_loc2, com1_receive_loc3, com1_receive_loc6, com1_process, com1_store,
                               com1_loc4_send}, label="Location 4",
                    scales=scales, demand_scale_level=2, capacity_scale_level=1, availability_scale_level=1,
                    capacity_factor={com1_process: scen_df[[('loc4', 'com1_process')]] if ('loc4',
                                                                                           'com1_process') in scen_df else default_df})

    loc5 = Location(name='loc5',
                    processes={com1_receive_loc1, com1_receive_loc2, com1_receive_loc4, com1_receive_loc7, com1_process,
                               com1_store, com1_loc5_send,
                               com1_sell}, label="Location 5", scales=scales, demand_scale_level=2,
                    capacity_scale_level=1, availability_scale_level=1,
                    capacity_factor={com1_process: scen_df[[('loc5', 'com1_process')]] if ('loc5',
                                                                                           'com1_process') in scen_df else default_df})

    loc6 = Location(name='loc6', processes={com1_procure, com1_process, com1_store, com1_loc6_send}, label="Location 6",
                    scales=scales, demand_scale_level=2, capacity_scale_level=1, availability_scale_level=1,
                    availability_factor={
                        com1_pur: scen_df[[('loc6', 'com1_pur')]] if ('loc6', 'com1_pur') in scen_df else default_df},
                    capacity_factor={com1_process: scen_df[[('loc6', 'com1_process')]] if ('loc6',
                                                                                           'com1_process') in scen_df else default_df})

    loc7 = Location(name='loc7', processes={com1_receive_loc4, com1_process, com1_store, com1_loc7_send},
                    label="Location 7",
                    scales=scales, demand_scale_level=2, capacity_scale_level=1, availability_scale_level=1,
                    capacity_factor={com1_process: scen_df[[('loc7', 'com1_process')]] if ('loc7',
                                                                                           'com1_process') in scen_df else default_df})

    # ======================================================================================================================
    # Declare transport/trucks
    # ======================================================================================================================

    truck_cap12 = 140 * capacity_scale_factor
    truck_cap13 = 60
    truck_cap24 = 100 * capacity_scale_factor
    truck_cap25 = 60 * capacity_scale_factor
    truck_cap34 = 60
    truck_cap45 = 200 * capacity_scale_factor
    truck_cap47 = 80 * capacity_scale_factor
    truck_cap64 = 100 * capacity_scale_factor
    truck_cap75 = 80 * capacity_scale_factor
    plane_cap15 = 30

    truck_capmin = 0.01
    plane_capmin = 0.01

    truck12 = Transport(name='truck12', resources={com1_loc1_out}, trans_max=truck_cap12,
                        label='Truck from location 1 to 2',
                        capex=0.5, vopex=0.05, trans_min=truck_capmin,
                        varying=[VaryingTransport.DETERMINISTIC_CAPACITY])
    # truck21 = Transport(name='truck21', resources={com1_loc2_out}, trans_max=truck_cap12, label='Truck from location 2 to 1', capex=0.0001, vopex=0.05, trans_min=truck_capmin, speed=50, varying=[VaryingTransport.DETERMINISTIC_CAPACITY])

    truck13 = Transport(name='truck13', resources={com1_loc1_out}, trans_max=truck_cap13,
                        label='Truck from location 1 to 3',
                        capex=0.3, vopex=0.03, trans_min=truck_capmin,
                        varying=[VaryingTransport.DETERMINISTIC_CAPACITY])
    # truck31 = Transport(name='truck31', resources={com1_loc3_out}, trans_max=truck_cap13, label='Truck from location 3 to 1', capex=0.0001, vopex=0.03, trans_min=truck_capmin, speed=50, varying=[VaryingTransport.DETERMINISTIC_CAPACITY])

    truck24 = Transport(name='truck24', resources={com1_loc2_out}, trans_max=truck_cap24,
                        label='Truck from location 2 to 4',
                        capex=0.5, vopex=0.05, trans_min=truck_capmin,
                        varying=[VaryingTransport.DETERMINISTIC_CAPACITY])
    # truck42 = Transport(name='truck42', resources={com1_loc4_out}, trans_max=truck_cap24, label='Truck from location 4 to 2', capex=0.0001, vopex=0.05, trans_min=truck_capmin, speed=50, varying=[VaryingTransport.DETERMINISTIC_CAPACITY])

    truck25 = Transport(name='truck25', resources={com1_loc2_out}, trans_max=truck_cap25,
                        label='Truck from location 2 to 5',
                        capex=0.3, vopex=0.03, trans_min=truck_capmin,
                        varying=[VaryingTransport.DETERMINISTIC_CAPACITY])
    # truck52 = Transport(name='truck52', resources={com1_loc5_out}, trans_max=truck_cap25, label='Truck from location 5 to 2', capex=0.0001, vopex=0.03, trans_min=truck_capmin, speed=50, varying=[VaryingTransport.DETERMINISTIC_CAPACITY])

    truck34 = Transport(name='truck34', resources={com1_loc3_out}, trans_max=truck_cap34,
                        label='Truck from location 3 to 4',
                        capex=0.2, vopex=0.02, trans_min=truck_capmin,
                        varying=[VaryingTransport.DETERMINISTIC_CAPACITY])
    # truck43 = Transport(name='truck43', resources={com1_loc4_out}, trans_max=truck_cap34, label='Truck from location 4 to 3', capex=0.0001, vopex=0.02, trans_min=truck_capmin, speed=50, varying=[VaryingTransport.DETERMINISTIC_CAPACITY])

    truck45 = Transport(name='truck45', resources={com1_loc4_out}, trans_max=truck_cap45,
                        label='Truck from location 4 to 5',
                        capex=1, vopex=0.1, trans_min=truck_capmin,
                        varying=[VaryingTransport.DETERMINISTIC_CAPACITY])
    # truck54 = Transport(name='truck54', resources={com1_loc5_out}, trans_max=truck_cap45, label='Truck from location 5 to 4', capex=0.0001, vopex=0.1, trans_min=truck_capmin, speed=50, varying=[VaryingTransport.DETERMINISTIC_CAPACITY])

    truck47 = Transport(name='truck47', resources={com1_loc4_out}, trans_max=truck_cap47,
                        label='Truck from location 4 to 7',
                        capex=0.4, vopex=0.04, trans_min=truck_capmin,
                        varying=[VaryingTransport.DETERMINISTIC_CAPACITY])
    # truck74 = Transport(name='truck74', resources={com1_loc7_out}, trans_max=truck_cap47, label='Truck from location 7 to 4', capex=0.0001, vopex=0.04, trans_min=truck_capmin, speed=50, varying=[VaryingTransport.DETERMINISTIC_CAPACITY])

    truck64 = Transport(name='truck64', resources={com1_loc6_out}, trans_max=truck_cap64,
                        label='Truck from location 6 to 4',
                        capex=0.5, vopex=0.05, trans_min=truck_capmin,
                        varying=[VaryingTransport.DETERMINISTIC_CAPACITY])
    # truck46 = Transport(name='truck46', resources={com1_loc4_out}, trans_max=truck_cap64, label='Truck from location 4 to 6', capex=0.0001, vopex=0.05, trans_min=truck_capmin, speed=50, varying=[VaryingTransport.DETERMINISTIC_CAPACITY])

    truck75 = Transport(name='truck75', resources={com1_loc7_out}, trans_max=truck_cap75,
                        label='Truck from location 7 to 5',
                        capex=0.4, vopex=0.04, trans_min=truck_capmin,
                        varying=[VaryingTransport.DETERMINISTIC_CAPACITY])
    # truck57 = Transport(name='truck57', resources={com1_loc5_out}, trans_max=truck_cap75, label='Truck from location 5 to 7', capex=0.0001, vopex=0.04, trans_min=truck_capmin, speed=50, varying=[VaryingTransport.DETERMINISTIC_CAPACITY])

    plane15 = Transport(name='plane15', resources={com1_loc1_out}, trans_max=plane_cap15,
                        label='Plane from location 1 to 5',
                        capex=3, vopex=0.5, trans_min=plane_capmin,
                        varying=[VaryingTransport.DETERMINISTIC_CAPACITY])

    # ======================================================================================================================
    # Declare network
    # ======================================================================================================================

    transport_matrix = [
        [[], [truck12], [truck13], [], [plane15], [], []],  # source: location 1
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
        [0, 55, 196, M, 130, M, M],
        [55, 0, M, 163, 112, M, 134],
        [196, M, 0, 63, M, M, M],
        [M, 163, 63, 0, 95, 117, 88],
        [130, 112, M, 95, 0, 150, 134],
        [M, M, M, 117, M, 0, M],
        [M, 134, M, 88, 134, M, 0]
    ]

    locset = [loc1, loc2, loc3, loc4, loc5, loc6, loc7]

    sources = locset
    sinks = locset

    network = Network(name='Network', scales=scales, source_locations=sources, sink_locations=sinks,
                      transport_matrix=transport_matrix, distance_matrix=distance_matrix,
                      transport_capacity_scale_level=1,
                      transport_capacity_factor={
                          (loc1, loc2): {truck12: scen_df[[('truck12', 'com1_loc1_out')]] if ('truck12',
                                                                                              'com1_loc1_out') in scen_df else default_df},
                          (loc1, loc3): {truck13: scen_df[[('truck13', 'com1_loc1_out')]] if ('truck13',
                                                                                              'com1_loc1_out') in scen_df else default_df},
                          (loc1, loc5): {plane15: scen_df[[('plane15', 'com1_loc1_out')]] if ('plane15',
                                                                                              'com1_loc1_out') in scen_df else default_df},
                          (loc2, loc4): {truck24: scen_df[[('truck24', 'com1_loc2_out')]] if ('truck24',
                                                                                              'com1_loc2_out') in scen_df else default_df},
                          (loc2, loc5): {truck25: scen_df[[('truck25', 'com1_loc2_out')]] if ('truck25',
                                                                                              'com1_loc2_out') in scen_df else default_df},
                          (loc3, loc4): {truck34: scen_df[[('truck34', 'com1_loc3_out')]] if ('truck34',
                                                                                              'com1_loc3_out') in scen_df else default_df},
                          (loc4, loc5): {truck45: scen_df[[('truck45', 'com1_loc4_out')]] if ('truck45',
                                                                                              'com1_loc4_out') in scen_df else default_df},
                          (loc4, loc7): {truck47: scen_df[[('truck47', 'com1_loc4_out')]] if ('truck47',
                                                                                              'com1_loc4_out') in scen_df else default_df},
                          (loc6, loc4): {truck64: scen_df[[('truck64', 'com1_loc6_out')]] if ('truck64',
                                                                                              'com1_loc6_out') in scen_df else default_df},
                          (loc7, loc5): {truck75: scen_df[[('truck75', 'com1_loc7_out')]] if ('truck75',
                                                                                              'com1_loc7_out') in scen_df else default_df},
                      })

    # ======================================================================================================================
    # Declare scenario
    # ======================================================================================================================

    daily_demand = 100
    demand_penalty = 75
    backlog_penalty = 50

    demand_dict = {i: {com1_sold: daily_demand} if i == loc5 else {com1_sold: 0} for i in locset}
    demand_penalty_dict = {i: {com1_sold: demand_penalty} if i == loc5 else {com1_sold: 0} for i in locset}
    backlog_penalty_dict = {i: {com1_sold: backlog_penalty} if i == loc5 else {com1_sold: 0} for i in locset}

    backlog_zero = {loc5: {com1_sold: 34}}

    scenario = Scenario(name=f'design scenario', label='Design Scenario',
                        annualization_factor=design_annualization_factor, scales=scales,
                        scheduling_scale_level=2, network_scale_level=0, purchase_scale_level=2,
                        availability_scale_level=1, demand_scale_level=2, capacity_scale_level=1,
                        network=network, demand=demand_dict, demand_penalty=demand_penalty_dict,
                        backlog_penalty=backlog_penalty_dict)

    if scen_df.empty:
        # ======================================================================================================================
        # Declare problem
        # ======================================================================================================================

        problem_mincost = formulate(scenario=scenario, demand_sign='eq', objective=Objective.COST_W_DEMAND_PENALTY,
                                    backlog_zero=backlog_zero,
                                    constraints={Constraints.COST, Constraints.TRANSPORT, Constraints.RESOURCE_BALANCE,
                                                 Constraints.INVENTORY, Constraints.PRODUCTION, Constraints.BACKLOG,
                                                 Constraints.NETWORK})

        scale_iter = scale_tuple(instance=problem_mincost, scale_levels=scenario.network_scale_level + 1)
        problem_mincost.first_stage_cost = Var(within=NonNegativeReals, doc='First Stage Cost')

        def first_stage_cost_rule(instance):
            return (instance.first_stage_cost == sum(instance.Capex_network[scale_] for scale_ in scale_iter) +
                    sum(instance.Capex_transport_network[scale_] for scale_ in scale_iter))

        problem_mincost.constraint_first_stage_cost = Constraint(rule=first_stage_cost_rule)

        return scenario, problem_mincost
    else:
        return scenario
def build_design_smodel(scen_df=pandas.DataFrame(), eps: float = 1.0):
    scenario = build_design_model(scen_df=scen_df, eps=eps)
    # ======================================================================================================================
    # Declare problem
    # ======================================================================================================================

    problem_mincost = formulate(scenario=scenario,
                                constraints={Constraints.COST, Constraints.TRANSPORT, Constraints.RESOURCE_BALANCE,
                                             Constraints.INVENTORY, Constraints.PRODUCTION, Constraints.DEMAND,
                                             Constraints.NETWORK},
                                demand_sign='eq', objective=Objective.COST_W_DEMAND_PENALTY)

    # demand = scenario.demand
    # if isinstance(demand, dict):
    #     if isinstance(list(demand.keys())[0], Location):
    #         try:
    #             demand = {i.name: {
    #                 j.name: demand[i][j] for j in demand[i].keys()} for i in demand.keys()}
    #         except:
    #             pass
    #
    # constraint_demand_lb(instance=problem_mincost, demand=demand, demand_factor=scenario.demand_factor,
    #                      demand_scale_level=scenario.demand_scale_level,
    #                      scheduling_scale_level=scenario.scheduling_scale_level,
    #                      location_resource_dict=scenario.location_resource_dict, epsilon=eps)

    scale_iter = scale_tuple(instance=problem_mincost, scale_levels=scenario.network_scale_level + 1)
    problem_mincost.first_stage_cost = Var(within=NonNegativeReals, doc='First Stage Cost')

    def first_stage_cost_rule(instance):
        return (instance.first_stage_cost == sum(instance.Capex_network[scale_] for scale_ in scale_iter) +
                sum(instance.Capex_transport_network[scale_] for scale_ in scale_iter))

    problem_mincost.constraint_first_stage_cost = Constraint(rule=first_stage_cost_rule)

    return scenario, problem_mincost

def design_scenario_creator(scen_name, **kwargs):
    scen_dict = kwargs.get('scenario_dict')
    # eps = kwargs.get('epsilon')
    fsv = kwargs.get('fsv')
    scen, model = build_design_smodel(scen_df=scen_dict[scen_name]['factor'])
    sputils.attach_root_node(model, model.first_stage_cost, list(getattr(model, v) for v in fsv))
    model._mpisppy_probability = scen_dict[scen_name]['prob']
    return model

if __name__ =='__main__':

    with open('scenario_dict_Backlog_EF.pkl', 'rb') as file:
        load_scenario_dict = pickle.load(file)

    load_scenario_names = list(load_scenario_dict.keys())
    print(f"Sum of probabilities of all scenarios: {sum(load_scenario_dict[scen]['prob'] for scen in load_scenario_dict):.6f}")
    print(f'Number of considered scenarios: {len(load_scenario_names)}')

    first_stage_variables = ('X_P', 'X_S', 'X_F', 'Cap_P', 'Cap_S', 'Cap_F')
    options = {"solver": "gurobi"}
    solver_options = {
        'MIPGap': 0.0005,
        'Heuristics': 0.20
    }
    scenario_creator_kwargs = {'scenario_dict': load_scenario_dict,
                               'fsv': first_stage_variables}

    start_time = time.time()
    ef_UI = ExtensiveForm(options, load_scenario_names, design_scenario_creator,
                          scenario_creator_kwargs=scenario_creator_kwargs)
    results = ef_UI.solve_extensive_form(solver_options=solver_options)
    end_time = time.time()

    exCost_UI = ef_UI.get_objective_value()
    ssoln_UI = ef_UI.get_root_solution()

    with open(f"ssoln_Backlog_EF.pkl", "wb") as file:
        pickle.dump(ssoln_UI, file)

    output_dict = dict()
    for scen in load_scenario_names:
        model_vars = getattr(ef_UI.ef, scen).component_map(ctype=Var)
        vars_dict = {i:model_vars[i].extract_values() for i in model_vars.keys()}

        model_obj = getattr(ef_UI.ef, scen).component_map(ctype=Objective)
        obj_dict = {'objective': model_obj[i]() for i in model_obj.keys()}

        output_dict[scen] ={**vars_dict, **obj_dict}

    with open(f'output_{len(load_scenario_names)}_Backlog_EF.pkl','wb') as file:
        pickle.dump(output_dict,file)

    exPen = 0
    for scen in load_scenario_names:
        model = getattr(ef_UI.ef, scen)
        exPen += pyoval(model.Demand_penalty_network[('com1_sold', 0)]) * load_scenario_dict[scen]['prob']

    fsc = pyoval(getattr(ef_UI.ef, load_scenario_names[0]).first_stage_cost)

    print(f'Total Expected Cost considering disruptions: {exCost_UI:.4f}')
    print(f'First Stage Cost: {fsc:.4f}')
    print(f'Execution time: {start_time - end_time:.4f} seconds')

    final_results_dict = {'Expected Cost UI': exCost_UI,
                          'First Stage Cost': fsc,
                          'Total Expected Penalty Cost': exPen,
                          'Execution Time': start_time - end_time}

    with open(f"final_results_Backlog_EF.pkl", 'wb') as file:
        pickle.dump(final_results_dict, file)