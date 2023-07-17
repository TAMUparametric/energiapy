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
from energiapy.model.solve import solve

# ======================================================================================================================
# Initialize Case Study
# ======================================================================================================================
_time_intervals = 10  # Number of time intervals in a planning horizon    (L_chi)
_exec_scenarios = 1  # Number of execution scenarios                     (chi)

M = 1e7  # Big M

# Define temporal scales
scales = TemporalScale(discretization_list=[_exec_scenarios, _time_intervals])

# ======================================================================================================================
# Declare resources/commodities
# ======================================================================================================================

com_cons = Resource(name='com_cons', cons_max=M, block={'imp': 1, 'urg': 1}, price=7.50,
                    label='Commodity consumed from outside the system')

com1 = Resource(name='com1', demand=True, sell=True, block={'imp': 1, 'urg': 1}, revenue=10.00,
                label='Commodity 1')

# ======================================================================================================================
# Declare processes/storage capacities
# ======================================================================================================================

procure = Process(name='procure', prod_max=M, conversion={com_cons: -1, com1: 1}, capex=0, vopex=0, fopex=0,
                  label='Procure com1')

store20 = Process(name='store20', storage=com1, store_max=20, prod_max=M, capex=2000, vopex=20,
                  label="Storage capacity of 20 units")
store50 = Process(name='store50', storage=com1, store_max=50, prod_max=M, capex=5000, vopex=50,
                  label="Storage capacity of 50 units")

# ======================================================================================================================
# Declare locations/warehouses
# ======================================================================================================================
loc1 = Location(name='loc1', processes={procure, store50}, label="Location 1", scales=scales, demand_scale_level=1,
                capacity_scale_level=1, availability_scale_level=1)
loc2 = Location(name='loc2', processes={store20}, label="Location 2", scales=scales, demand_scale_level=1,
                capacity_scale_level=1, availability_scale_level=1)
loc3 = Location(name='loc3', processes={store20}, label="Location 3", scales=scales, demand_scale_level=1,
                capacity_scale_level=1, availability_scale_level=1)

# ======================================================================================================================
# Declare transport/trucks
# ======================================================================================================================
truck100 = Transport(name='truck100', resources=[com1], trans_max=100, label='Truck with maximum capacity of 100 units',
                     trans_cost=0.1)

transport_matrix = [
    [[], [truck100], []],  # sink: location 1
    [[truck100], [], [truck100]],  # sink: location 2
    [[], [truck100], []]  # sink: location 3
]

distance_matrix = [
    [0, 10, 0],
    [10, 0, 10],
    [0, 10, 0]
]

# ======================================================================================================================
# Declare network
# ======================================================================================================================
locset = {loc1, loc2, loc3}

sources = list(locset)
sinks = list(locset)

network = Network(name='Network', source_locations=sources, sink_locations=sinks, transport_matrix=transport_matrix,
                  distance_matrix=distance_matrix)

# ======================================================================================================================
# Declare scenario
# ======================================================================================================================
demand_dict = {i: {com1: 75} if i == loc3 else {com1: 0} for i in locset}

scenario = Scenario(name='scenario', scales=scales, scheduling_scale_level=1, network_scale_level=0,
                    purchase_scale_level=1,
                    demand_scale_level=1, network=network, demand=demand_dict, label='scenario')

problem = formulate(scenario=scenario, constraints={Constraints.COST, Constraints.TRANSPORT,
                                                    Constraints.RESOURCE_BALANCE, Constraints.PRODUCTION,
                                                    Constraints.INVENTORY},
                    objective=Objective.COST)

results = solve(scenario=scenario, instance=problem, solver='gurobi', name='LP')
