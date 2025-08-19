from pyomo.environ import *
import os
import sys

sys.path.append('/scratch/user/shivam.vedant')
sys.path.append('/scratch/user/shivam.vedant/src')
# sys.path.append('../../../../../../src')

import pandas
# import random
# import math
# from itertools import product
# from functools import reduce
from energiapy.components.temporal_scale import TemporalScale
from energiapy.components.resource import Resource, VaryingResource
from energiapy.components.process import Process, VaryingProcess
from energiapy.components.location import Location
from energiapy.components.transport import Transport, VaryingTransport
from energiapy.components.network import Network
from energiapy.components.scenario import Scenario
from energiapy.model.constraints.demand import constraint_demand_lb
# from energiapy.components.result import Result
from energiapy.model.formulate import formulate, Constraints, Objective
# from energiapy.plot import plot_results, plot_scenario, plot_location
# from energiapy.model.solve import solve
# from pyomo.environ import Param
from pyomo.environ import value as pyoval
# from collections import defaultdict
from energiapy.utils.scale_utils import scale_tuple
# import matplotlib.pyplot as plt
# from matplotlib import rc
# from typing import Union, Tuple, List
from pyomo.environ import Var, Constraint, NonNegativeReals
# from pyomo.contrib.iis import write_iis
import time
import pickle
# from energiapy.model.constraints.constraints import make_constraint, Cons
# from energiapy.model.formulate import constraint_export, constraint_demand_penalty, constraint_demand_penalty_cost

import mpisppy.utils.sputils as sputils
from mpisppy.opt.ef import ExtensiveForm

_coms = 1

design_planning_horizons = 1
# design_exec_scenarios = 52
design_scale_factor = 1

capacity_scale_factor = 1

schedule_planning_horizons = 1
schedule_exec_scenarios = 52
schedule_time_intervals = 7

M = 1e3  # Big M

design_annualization_factor = 1/design_planning_horizons
# schedule_annualization_factor = 1/schedule_planning_horizons

fill_rate = 0.6
# fill_rate = float(sys.argv[1])

print(f"fill_rate: {fill_rate}")
print(f"Type: {type(fill_rate)}")

if __name__ == '__main__':
    with open('scenario_dict_EF.pkl', 'rb') as file:
        load_scenario_dict = pickle.load(file)

    load_scenario_names = list(load_scenario_dict.keys())

    print(
        f"Sum of probabilities of all scenarios: {sum(load_scenario_dict[scen]['prob'] for scen in load_scenario_dict):.6f}")
    print(f'Number of considered scenarios: {len(load_scenario_names)}')