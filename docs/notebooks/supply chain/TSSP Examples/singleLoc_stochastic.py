from pyomo.environ import *
from pyomo.environ import Binary, NonNegativeReals, value
import mpisppy.utils.sputils as sputils
import matplotlib.pyplot as plt
from matplotlib import rc
import sys
sys.path.append('../../../../src')
import pandas
import random
import math
from energiapy.components.temporal_scale import TemporalScale
from energiapy.components.resource import Resource, VaryingResource
from energiapy.components.process import Process, ProcessMode, VaryingProcess
from energiapy.components.location import Location
from energiapy.components.transport import Transport
from energiapy.components.network import Network
from energiapy.components.scenario import Scenario
# from energiapy.model.constraints.demand import constraint_demand2
from energiapy.components.result import Result
from energiapy.model.formulate import formulate, Constraints, Objective
from energiapy.plot import plot_results, plot_scenario, plot_location
from energiapy.model.solve import solve
from pyomo.environ import Param
from energiapy.utils.scale_utils import scale_pyomo_set
from energiapy.utils.scale_utils import scale_list, scale_tuple
from mpisppy.opt.ef import ExtensiveForm
import pickle

#%%
_time_intervals = 7  # Number of time intervals in a planning horizon    (L_chi)
_coms = 1
_exec_scenarios = 52  # Number of execution scenarios                     (chi)

# M = 1e3  # Big M

all_scenario_names = ["good", "average", "bad"]
ns_dict = {'good': 52, "average": 26, "bad":0}
scenario_probabilities = {'good': 0.4, 'average': 0.3, 'bad': 0.3}

#%%

def build_model(cap_factor):
    # Define temporal scales
    scales = TemporalScale(discretization_list=[1, _exec_scenarios, _time_intervals])

    # ======================================================================================================================
    # Declare resources/commodities
    # ======================================================================================================================
    com1_pur = Resource(name='com1_pur', cons_max=500, block={'imp': 1, 'urg': 1}, price=0.00,
                        label='Commodity 1 consumed from outside the system')

    com1_in = Resource(name='com1_in', label='Commodity 1 received')
    com1_out = Resource(name='com1_out', label='Commodity 1 to be sent out')

    com1_loc1_out = Resource(name='com1_loc1_out', label='Commodity 1 sent out from location 1')
    # com1_loc2_out = Resource(name='com1_loc2_out', label='Commodity 1 sent out from location 2')

    com1_sold = Resource(name='com1_sold', revenue=0.00, demand=True, sell=True,
                         label='Commodity 1 sold to outside the system')

    # ======================================================================================================================
    # Declare processes/storage capacities
    # ======================================================================================================================
    com1_process_capacity = 250

    # prod_max = {0: 0.25*com1_process_capacity, 1: 0.5*com1_process_capacity, 2: 0.75*com1_process_capacity, 3: 0.95*com1_process_capacity, 4: com1_process_capacity}
    # prod_min = {0: 0, 1: 0.25*75, 2: 0.5*75, 3: 0.75*75, 4: 0.95*75}
    # rate_max = {0:1.25/2, 1: 1/2, 2: 0.75/2, 3: 0.5/2, 4: 0.25/2}
    # mode_ramp = {(0,1): 5, (1,2): 5}

    com1_procure = Process(name='procure com1', prod_max=com1_process_capacity, conversion={com1_pur: -1, com1_in: 1},
                           capex=0.1, vopex=0.1, prod_min=0.01, label='Procure com1',
                           varying=[VaryingProcess.DETERMINISTIC_CAPACITY], order_fopex=150)

    com1_sell = Process(name='sell com1', prod_max=com1_process_capacity, conversion={com1_out: -1, com1_sold: 1},
                        capex=0.1, vopex=0.1, prod_min=0.01, label='Sell com1')
    com1_opt_procure = Process(name='procure optional com1', prod_max=150, conversion={com1_pur: -1, com1_in: 1},
                               capex=10, vopex=0.1, prod_min=0.01, label='Procure optional com1', order_fopex=200)

    com1_receive_loc1 = Process(name='com1_receive_loc1', prod_max=com1_process_capacity,
                                conversion={com1_loc1_out: -1, com1_in: 1}, capex=0.1, vopex=0.01, prod_min=0.01,
                                label='Commodity 1 received from location 1')
    # com1_receive_loc2 = Process(name='com1_receive_loc2', prod_max=com1_process_capacity, conversion={com1_loc2_out:-1, com1_in:1}, capex=0.01, vopex=0.01, prod_min=com1_process_capacity, label='Commodity 1 received from location 2')

    # com1_process = Process(name='com1_process', prod_max=com1_process_capacity, conversion={com1_in: -1, com1_out: 1},  capex=0.01, vopex=0.01, prod_min=com1_process_capacity, label='Process the commodity through the location')

    com1_process = Process(name='com1_process', prod_max=com1_process_capacity, conversion={com1_in: -1, com1_out: 1},
                           capex=0.1, vopex=0.01, prod_min=com1_process_capacity,
                           label='Process the commodity through the location')

    # com1_process = Process(name='com1_process', prod_max=prod_max, conversion={0: {com1_in: -1, com1_out: 1}, 1: {com1_in: -1, com1_out: 1}, 2: {com1_in: -1, com1_out: 1}, 3: {com1_in: -1, com1_out: 1}, 4: {com1_in: -1, com1_out: 1}},  capex=0.1, vopex=0.01, prod_min=prod_min, label='Process the commodity through the location', rate_max=rate_max)

    com1_store = Process(name='com1_store', prod_max=com1_process_capacity, capex=0.1, vopex=0.05, storage_capex=0.5,
                         store_min=0.01, store_max=200, prod_min=0.01, label="Storage capacity of 200 units",
                         storage=com1_in, storage_cost=0.02)

    # com1_store10 = Process(name='com1_store10', prod_max=com1_process_capacity, capex=0.1, vopex=0.01, storage_capex=0.1, store_min=0.01, store_max= 40, prod_min=0.01, label="Storage capacity of 10 units", storage=com1_in, storage_cost=0.02)
    # com1_store20 = Process(name='com1_store20', prod_max=com1_process_capacity, capex=0.1, vopex=0.02, storage_capex=0.2, store_min=0.01, store_max= 80, prod_min=0.01, label="Storage capacity of 20 units", storage=com1_in, storage_cost=0.02)
    # com1_store50 = Process(name='com1_store50', prod_max=com1_process_capacity, capex=0.1, vopex=0.05, storage_capex=0.5, store_min=0.01, store_max= 200, prod_min=0.01, label="Storage capacity of 50 units", storage=com1_in, storage_cost=0.02)

    com1_loc1_send = Process(name='com1_loc1_send', prod_max=com1_process_capacity,
                             conversion={com1_out: -1, com1_loc1_out: 1}, capex=0.1, vopex=0.1, prod_min=0.01,
                             label='Send commodity one from location 1')
    # com1_loc2_send = Process(name='com1_loc2_send', prod_max=com1_process_capacity, conversion={com1_out:-1, com1_loc2_out:1}, capex=0.01, vopex=0.01, prod_min=com1_process_capacity, label='Send commodity one from location 2')

    # ======================================================================================================================
    # Declare locations/warehouses
    # ======================================================================================================================
    loc1 = Location(name='loc1',
                    processes={com1_procure, com1_process, com1_store, com1_loc1_send, com1_sell, com1_opt_procure},
                    label="Location 1", scales=scales, demand_scale_level=2, capacity_scale_level=1,
                    availability_scale_level=1, capacity_factor={com1_procure: cap_factor[['com1_procure']]})

    locset = [loc1]

    # ======================================================================================================================
    # Declare scenario
    # ======================================================================================================================

    daily_demand = 100
    demand_penalty = 20

    demand_dict = {i: {com1_sold: daily_demand} if i == loc1 else {com1_sold: 0} for i in locset}
    demand_penalty_dict = {i: {com1_sold: demand_penalty} if i == loc1 else {com1_sold: 0} for i in locset}

    scenario = Scenario(name='scenario_baseline', network=loc1, scales=scales, scheduling_scale_level=2,
                        network_scale_level=0, purchase_scale_level=2, availability_scale_level=1, demand_scale_level=2,
                        capacity_scale_level=1, demand=demand_dict, demand_penalty=demand_penalty_dict,
                        label='Scenario with perfect information')

    # ======================================================================================================================
    # Declare problem
    # ======================================================================================================================

    problem_mincost = formulate(scenario=scenario,
                                constraints={Constraints.COST, Constraints.RESOURCE_BALANCE, Constraints.INVENTORY,
                                             Constraints.PRODUCTION, Constraints.DEMAND, Constraints.NETWORK},
                                demand_sign='eq', objective=Objective.COST_W_DEMAND_PENALTY)

    scale_iter = scale_tuple(instance=problem_mincost, scale_levels=scenario.network_scale_level + 1)
    capex_process = sum(problem_mincost.Capex_network[scale_] for scale_ in scale_iter)

    problem_mincost.first_stage_cost = capex_process

    return scenario, problem_mincost

def scenario_creator(scenario_name):
    cap_factor_scen = pandas.DataFrame(data={'com1_procure': [1] * ns_dict[scenario_name] + [0] * (_exec_scenarios - ns_dict[scenario_name])})
    scen, model = build_model(cap_factor=cap_factor_scen)
    sputils.attach_root_node(model, model.first_stage_cost, [model.X_P, model.Cap_P, model.X_S, model.Cap_S])
    model._mpisppy_probability = scenario_probabilities[scenario_name]
    return model
#PERFECT INFORMATION

if __name__ == '__main__':
    exCost_PI = 0
    results_PI = dict()
    model_PI = dict()
    solver_options = {
        'MIPGap': 0.005,
        'TimeLimit': 60 * 15,
        'Heuristics': 0.20
    }

    for scenario_name in all_scenario_names:
        cap_factor = pandas.DataFrame(
            data={'com1_procure': [1] * ns_dict[scenario_name] + [0] * (_exec_scenarios - ns_dict[scenario_name])})
        scen_PI, model_PI[scenario_name] = build_model(cap_factor=cap_factor)
        results_PI[scenario_name] = solve(scenario=scen_PI, instance=model_PI[scenario_name], solver='gurobi',
                                          name=scenario_name, solver_options=solver_options, saveformat='.pkl')

        # print(f"################## OBJECTIVE VALUE: {value(model_PI.objective_cost_w_demand_penalty)} ##################")
        # print(f"################## NETWORK CAPEX: {value(model_PI.Capex_network[0])} ##################")
        # print(f"################## NETWORK VOPEX: {value(model_PI.Vopex_network[0])} ##################")
        # print(f"################## NETWORK InvHold: {value(model_PI.Inv_cost_network[0])} ##################")
        # print(f"################## DEMAND PENALTY: {value(model_PI.Demand_penalty_cost_network['com1_sold',0])} ##################")

        exCost_PI += value(model_PI[scenario_name].objective_cost_w_demand_penalty) * scenario_probabilities[scenario_name]


    options = {"solver": "gurobi"}
    ef_UI = ExtensiveForm(options, all_scenario_names, scenario_creator, model_name='model_UI')
    results = ef_UI.solve_extensive_form(solver_options=solver_options)

    UI_output_dict = dict()
    for scenario in all_scenario_names:
        model_vars = getattr(ef_UI.ef, scenario).component_map(ctype=Var)
        vars_dict = {i: model_vars[i].extract_values()
                     for i in model_vars.keys()}

        model_obj = getattr(ef_UI.ef, scenario).component_map(ctype=Objective)
        obj_dict = {'objective': model_obj[i]() for i in model_obj.keys()}

        UI_output_dict[scenario] = {**vars_dict, **obj_dict}

    with open('singleLoc_stochastic.pkl', "wb") as f:
        pickle.dump(UI_output_dict, f)
        f.close()

    results_dict = pickle.load(open('singleLoc_stochastic.pkl', "rb"))

    print(f"Expected cost under perfect information: {exCost_PI:.3f}")

    exCost_UI = ef_UI.get_objective_value()
    print(f"Expected cost under uncertainty: {exCost_UI:.3f}")

    EVPI = exCost_UI - exCost_PI
    print(f"Expected Value of Perfect Information: {EVPI:.3f}")

    for outer_key, inner_dict in results_dict.items():
        print(f"{outer_key}:")
        print('\n'.join([f"    {k}: {v}" for k, v in inner_dict.items()]))

    # print(results_dict, sep='\n')
