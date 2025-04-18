from pyomo.environ import *
import os
import sys
import time
import pickle

# sys.path.append('/scratch/user/shivam.vedant')
# sys.path.append('/scratch/user/shivam.vedant/src')
sys.path.append('../../../../../src')

import mpisppy.utils.sputils as sputils
from mpisppy.opt.lshaped import LShapedMethod

def build_model(yields):
    model = ConcreteModel()

    # Variables
    model.X = Var(["WHEAT", "CORN", "BEETS"], within=NonNegativeReals)
    model.Y = Var(["WHEAT", "CORN"], within=NonNegativeReals)
    model.W = Var(
        ["WHEAT", "CORN", "BEETS_FAVORABLE", "BEETS_UNFAVORABLE"],
        within=NonNegativeReals,
    )

    # Objective function
    # model.WHEAT_COST = 150 * model.X["WHEAT"]
    # model.CORN_COST = 230 * model.X["CORN"]
    # model.BEETS_COST = 260 * model.X["BEETS"]
    # model.PLANTING_COST = model.WHEAT_COST + model.CORN_COST + model.BEETS_COST
    model.PLANTING_COST = 150 * model.X["WHEAT"] + 230 * model.X["CORN"] + 260 * model.X["BEETS"]
    model.PURCHASE_COST = 238 * model.Y["WHEAT"] + 210 * model.Y["CORN"]
    model.SALES_REVENUE = (
        170 * model.W["WHEAT"] + 150 * model.W["CORN"]
        + 36 * model.W["BEETS_FAVORABLE"] + 10 * model.W["BEETS_UNFAVORABLE"]
    )
    model.OBJ = Objective(
        expr=model.PLANTING_COST + model.PURCHASE_COST - model.SALES_REVENUE,
        sense=minimize
    )

    # Constraints
    model.CONSTR= ConstraintList()

    model.CONSTR.add(summation(model.X) <= 500)
    model.CONSTR.add(
        yields[0] * model.X["WHEAT"] + model.Y["WHEAT"] - model.W["WHEAT"] >= 200
    )
    model.CONSTR.add(
        yields[1] * model.X["CORN"] + model.Y["CORN"] - model.W["CORN"] >= 240
    )
    model.CONSTR.add(
        yields[2] * model.X["BEETS"] - model.W["BEETS_FAVORABLE"] - model.W["BEETS_UNFAVORABLE"] >= 0
    )
    model.W["BEETS_FAVORABLE"].setub(6000)

    return model

def scenario_creator(scenario_name):
    if scenario_name == "good":
        yields = [3, 3.6, 24]
    elif scenario_name == "average":
        yields = [2.5, 3, 20]
    elif scenario_name == "bad":
        yields = [2, 2.4, 16]
    else:
        raise ValueError("Unrecognized scenario name")

    scenario_probabilities = {'good': 0.33, 'average': 0.33, 'bad':0.33}
    model = build_model(yields)
    sputils.attach_root_node(model, model.PLANTING_COST, [model.X])
    model._mpisppy_probability = 1.0/3
    # model.pprint()
    return model

if __name__ == "__main__":
    all_scenario_names = ["good", "average", "bad"]
    bounds = {name: -432000 for name in all_scenario_names}
    options = {
        "root_solver": "gurobi",
        "sp_solver": "gurobi",
        "sp_solver_options": {"threads": 1},
        # "valid_eta_lb": bounds,
        "max_iter": 10,
        # 'verbose': True,
    }

    fill_rate = float(sys.argv[1])
    print(fill_rate)
    print(type(fill_rate))

    start_time = time.time()
    ls = LShapedMethod(options, all_scenario_names, scenario_creator)
    result = ls.lshaped_algorithm()
    end_time = time.time()

    print(f'Execution Time: {(end_time - start_time):.2f} seconds')

    variables = ls.gather_var_values_to_rank0()
    # for ((scen_name, var_name), var_value) in variables.items():
    #     print(scen_name, var_name, var_value)

    with open(f'bdsoln_{len(all_scenario_names)}_{int(fill_rate * 10):02d}_UI.pkl', 'wb') as file:
        pickle.dump(variables, file)

    with open(f'bdsoln_{len(all_scenario_names)}_{int(fill_rate*10):02d}_UI.pkl', 'rb') as file:
        load_values = pickle.load(file)

    print(load_values)