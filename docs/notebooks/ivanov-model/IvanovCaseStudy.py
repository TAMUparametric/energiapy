"""
Ivanov Model as described in the publication
'Optimal distribution (re)planning in a centralized multi-stage supply network under conditions of the ripple effect
 and structure dynamics'

webpage link: https://www.sciencedirect.com/science/article/pii/S0377221714001386?via%3Dihub
"""

__author__ = "Shivam Vedant"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Shivam Vedant", "Natasha Jane Chrisandina", "Efstratios N. Pistikopoulos", "Eleftherios Iakovou",
               "Mahmoud M. El-Halwagi"]
__license__ = "Open"
__version__ = "0.0.1"
__maintainer__ = "Shivam Vedant"
__email__ = "shivam.vedant@tamu.edu"
__status__ = "Production"

# ======================================================================================================================
#                                                   Import Modules
# ======================================================================================================================
import sys

sys.path.append('../../src')
import energiapy
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
from energiapy.plot import plot_results, plot_scenario
from energiapy.model.solve import solve

# ======================================================================================================================
# Initialize Case Study
# ======================================================================================================================
start_time = 0  # Start time of the analysis                        (t0)
end_time = 1000  # End time of the analysis                          (tf)
_time_intervals = 10  # Number of time intervals in a planning horizon    (L_chi)
_commodities = 1  # Number of commodities                             (rho)
_exec_scenarios = 4  # Number of execution scenarios                     (chi)

M = 1e7  # Big M

availability_factor_com1 = pandas.DataFrame(data={'com_cons': [1,1,1,1]})

# Define temporal scales
scales = TemporalScale(discretization_list=[_exec_scenarios, _time_intervals])

# ======================================================================================================================
# Declare resources/commodities
# ======================================================================================================================

com_cons = Resource(name='com_cons', cons_max=M, block={'imp': 1, 'urg': 1}, price=7.50,
                    label='Commodity consumed from outside the system', varying=[VaryingResource.DETERMINISTIC_AVAILABILITY])

com1 = Resource(name='com1', demand=True, sell=True, block={'imp': 1, 'urg': 1}, revenue=10.00,
                label='Commodity 1')

# ======================================================================================================================
# Declare processes/storage capacities
# ======================================================================================================================
procure = Process(name='procure', prod_max=M, conversion={com_cons: -1, com1: 1}, capex=0, vopex=0, fopex=0,
                  label='Procure com1')

store10 = Process(name='store10', storage=com1, store_max=10, prod_max=M, capex=1000, vopex=10,
                  label="Storage capacity of 10 units")
store20 = Process(name='store20', storage=com1, store_max=20, prod_max=M, capex=2000, vopex=20,
                  label="Storage capacity of 20 units")
store50 = Process(name='store50', storage=com1, store_max=50, prod_max=M, capex=10000, vopex=50,
                  label="Storage capacity of 50 units")

# ======================================================================================================================
# Declare locations/warehouses
# ======================================================================================================================
loc1 = Location(name='loc1', processes={procure, store20}, label="Location 1", scales=scales, demand_scale_level=1,
                capacity_scale_level=0, availability_scale_level=0, availability_factor= {com_cons: availability_factor_com1})
loc2 = Location(name='loc2', processes={store20}, label="Location 2", scales=scales, demand_scale_level=1,
                capacity_scale_level=0, availability_scale_level=0)
loc3 = Location(name='loc3', processes={store20}, label="Location 3", scales=scales, demand_scale_level=1,
                capacity_scale_level=0, availability_scale_level=0)
loc4 = Location(name='loc4', processes={store50}, label="Location 4", scales=scales, demand_scale_level=1,
                capacity_scale_level=0, availability_scale_level=0)
loc5 = Location(name='loc5', processes={store50}, label="Location 5", scales=scales, demand_scale_level=1,
                capacity_scale_level=0, availability_scale_level=0)
loc6 = Location(name='loc6', processes={procure, store10}, label="Location 6", scales=scales, demand_scale_level=1,
                capacity_scale_level=0, availability_scale_level=0)
loc7 = Location(name='loc7', processes={store10}, label="Location 7", scales=scales, demand_scale_level=1,
                capacity_scale_level=0, availability_scale_level=0)

# ======================================================================================================================
# Declare transport/trucks
# ======================================================================================================================
truck20 = Transport(name='truck20', resources=[com1], trans_max=20, label='Truck with maximum capacity of 20 units',
                    trans_cost=0.02)
truck30 = Transport(name='truck30', resources=[com1], trans_max=30, label='Truck with maximum capacity of 30 units',
                    trans_cost=0.03)
truck40 = Transport(name='truck40', resources=[com1], trans_max=40, label='Truck with maximum capacity of 40 units',
                    trans_cost=0.04)
truck50 = Transport(name='truck50', resources=[com1], trans_max=50, label='Truck with maximum capacity of 50 units',
                    trans_cost=0.05)
truck100 = Transport(name='truck100', resources=[com1], trans_max=100, label='Truck with maximum capacity of 100 units',
                     trans_cost=0.1)

transport_matrix = [
    [[], [truck50], [truck30], [], [], [], []],  # sink: location 1
    [[truck50], [], [], [truck50], [truck30], [], []],  # sink: location 2
    [[truck30], [], [], [truck20], [], [], []],  # sink: location 3
    [[], [truck50], [truck20], [], [truck100], [truck50], [truck40]],  # sink: location 4
    [[], [truck30], [], [truck100], [], [], [truck40]],  # sink: location 5
    [[], [], [], [truck50], [], [], []],  # sink: location 6
    [[], [], [], [truck40], [truck40], [], []]  # sink: location 7
]

distance_matrix = [
    [0, 100, 100, 100, 100, 100, 100],
    [100, 0, 100, 100, 100, 100, 100],
    [100, 100, 0, 100, 100, 100, 100],
    [100, 100, 100, 0, 100, 100, 100],
    [100, 100, 100, 100, 0, 100, 100],
    [100, 100, 100, 100, 100, 0, 100],
    [100, 100, 100, 100, 100, 100, 0]
]

# ======================================================================================================================
# Declare network
# ======================================================================================================================
locset = [loc1, loc2, loc3, loc4, loc5, loc6, loc7]

sources = list(locset)
sinks = list(locset)

network = Network(name='Network', source_locations=sources, sink_locations=sinks, transport_matrix=transport_matrix,
                  distance_matrix=distance_matrix)

demand_dict = {i: {com1: 100} if i == loc5 else {com1: 0} for i in locset}

scenario = Scenario(name='scenario', scales=scales, scheduling_scale_level=1, network_scale_level=0,
                    purchase_scale_level=1,
                    demand_scale_level=1, network=network, demand=demand_dict, label='scenario')

problem = formulate(scenario=scenario, constraints={Constraints.COST, Constraints.TRANSPORT,
                                                    Constraints.RESOURCE_BALANCE, Constraints.PRODUCTION,
                                                    Constraints.INVENTORY},
                    objective=Objective.COST)

results = solve(scenario=scenario, instance=problem, solver='gurobi', name='MILP')
