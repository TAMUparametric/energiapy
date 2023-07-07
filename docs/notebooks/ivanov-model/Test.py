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
_commodities = 1  # Number of commodities                             (rho)
_exec_scenarios = 2  # Number of execution scenarios                     (chi)

M = 1e7  # Big M

# Define temporal scales
scales = TemporalScale(discretization_list=[_exec_scenarios, _time_intervals])

# ======================================================================================================================
# Declare resources/commodities
# ======================================================================================================================

com1 = Resource(name='com1', cons_max=M, demand=True, sell=True, revenue= 10.00, price= 7.50,
                block={'imp': 1, 'urg': 1}, label='Commodity 1', store_max=M)

# ======================================================================================================================
# Declare processes/storage capacities
# ======================================================================================================================
store50 = Process(name='store10', storage=com1, store_max=50, prod_max=M, conversion={com1: -1, com1: 1}, capex=5000,
                  label="Storage capacity of 10 units")
store20 = Process(name='store20', storage=com1, store_max=20, prod_max=M, conversion={com1: -1, com1: 1}, capex=2000,
                  label="Storage capacity of 20 units")