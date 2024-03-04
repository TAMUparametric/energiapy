

# %%
# # %%

import sys
sys.path.append('../../')
import pandas
from src.energiapy.components.resource import Resource, VaryingResource
from src.energiapy.components.temporal_scale import TemporalScale
from src.energiapy.components.process import Process, VaryingProcess
from src.energiapy.components.material import Material
from src.energiapy.components.location import Location
from src.energiapy.components.scenario import Scenario
from src.energiapy.model.formulate import formulate, Constraints, Objective
from src.energiapy.model.solve import solve



# #%%

demand_factor = pandas.DataFrame(data={'Value': [0.5, 1, 0.5, 0.25]})
capacity_factor = pandas.DataFrame(data={'Value': [1, 0.5, 1, 0.25]})
availability_factor = pandas.DataFrame(data={'Value': [1, 1, 0.5, 0.5]})
price_factor = pandas.DataFrame(data={'Value': [0.25, 1, 0.5, 0.75]})
revenue_factor = pandas.DataFrame(data={'Value': [0.25, 1, 0.25, 0.5]})

scales = TemporalScale(discretization_list=[1, 4])

Resource_certain_availability = Resource(
    name='resource_certain_availability', cons_max=100, price=2)

Resource_deterministic_availability = Resource(name='resource_deterministic_availability', cons_max=100, price=5, varying=[
                                               VaryingResource.DETERMINISTIC_AVAILABILITY])
Resource_deterministic_demand = Resource(name='resource_deterministic_demand', demand=True, varying=[
                                         VaryingResource.DETERMINISTIC_DEMAND])
Resource_deterministic_price = Resource(name='resource_deterministic_price', cons_max=100, price=10, varying=[
                                        VaryingResource.DETERMINISTIC_PRICE])
Resource_deterministic_revenue = Resource(name='resource_deterministic_revenue', demand=True, revenue=500, varying=[
                                          VaryingResource.DETERMINISTIC_REVENUE])

Process_deterministic_capacity = Process(name='process_deterministic_capacity', conversion={Resource_certain_availability: -1, Resource_deterministic_demand: 1},
                                         capex=1000, fopex=10, vopex=1, prod_max=100, prod_min=0, varying=[VaryingProcess.DETERMINISTIC_CAPACITY])
Process_certain_capacity = Process(name='process_certain_capacity', conversion={
                                   Resource_deterministic_demand: -0.5, Resource_deterministic_availability: -0.5, Resource_deterministic_price: -0.25, Resource_deterministic_revenue: 1},
                                   capex=100, fopex=10, vopex=1, prod_max=100, prod_min=0)
Process_storage = Process(name='process_storage', storage=Resource_deterministic_demand,
                          capex=100, fopex=5, vopex=0.5, prod_max=50, prod_min=0, store_max=25, storage_cost=0.1)

Place = Location(name='location', processes={Process_certain_capacity, Process_deterministic_capacity, Process_storage}, scales=scales,
                 demand_scale_level=1, capacity_scale_level=1, price_scale_level=1, availability_scale_level=1,
                 demand_factor={Resource_deterministic_demand: demand_factor}, capacity_factor={Process_deterministic_capacity: capacity_factor},
                 price_factor={Resource_deterministic_price: price_factor}, availability_factor={Resource_deterministic_availability: availability_factor},
                 revenue_factor={Resource_deterministic_revenue: revenue_factor})

Occurance = Scenario(name='scenario', scales=scales, network=Place, demand_scale_level=1, network_scale_level=0, scheduling_scale_level=1,
                     capacity_scale_level=1, purchase_scale_level=1, availability_scale_level=1,
                     demand={Place: {Resource_deterministic_demand: 25, Resource_deterministic_revenue: 25}})

# LP = formulate(scenario=Occurance, constraints={Constraints.COST, Constraints.INVENTORY,
#                Constraints.PRODUCTION, Constraints.RESOURCE_BALANCE, Constraints.DEMAND}, objective=Objective.COST)
LP = formulate(scenario=Occurance, constraints={Constraints.COST, Constraints.INVENTORY,
               Constraints.PRODUCTION, Constraints.RESOURCE_BALANCE}, objective=Objective.PROFIT)

results = solve(scenario=Occurance, instance=LP, solver='gurobi', name='LP')

# %%


demand_factor = pandas.DataFrame(data={'Value': [0.5, 1, 0.5, 0.25]})
capacity_factor = pandas.DataFrame(data={'Value': [1, 0.5, 1, 0.25]})
capacity_factor2 = pandas.DataFrame(data={'Value': [0.75, 1, 0.25, 0.5]})
availability_factor = pandas.DataFrame(data={'Value': [1, 1, 0.5, 0.5]})
price_factor = pandas.DataFrame(data={'Value': [0.25, 1, 0.5, 0.75]})
revenue_factor = pandas.DataFrame(data={'Value': [0.25, 1, 0.25, 0.5]})

scales = TemporalScale(discretization_list=[1, 4])

Resource_certain_availability = Resource(
    name='resource_certain_availability', cons_max=100, price=2)

Resource_deterministic_availability = Resource(name='resource_deterministic_availability', cons_max=100, price=5, varying=[
                                               VaryingResource.DETERMINISTIC_AVAILABILITY])
Resource_deterministic_demand = Resource(name='resource_deterministic_demand', demand=True, varying=[
                                         VaryingResource.DETERMINISTIC_DEMAND])
Resource_deterministic_price = Resource(name='resource_deterministic_price', cons_max=100, price=10, varying=[
                                        VaryingResource.DETERMINISTIC_PRICE])
Resource_deterministic_revenue = Resource(name='resource_deterministic_revenue', demand=True, revenue=500, varying=[
                                          VaryingResource.DETERMINISTIC_REVENUE])

Process_deterministic_capacity = Process(name='process_deterministic_capacity', conversion={Resource_certain_availability: -1, Resource_deterministic_demand: 1},
                                         capex=1000, fopex=10, vopex=1, prod_max=100, prod_min=10, varying=[VaryingProcess.DETERMINISTIC_CAPACITY])

Process_deterministic_capacity2 = Process(name='process_deterministic_capacity2', conversion={Resource_certain_availability: -1, Resource_deterministic_demand: 1},
                                         capex=2000, fopex=20, vopex=5, prod_max=100, prod_min=10, varying=[VaryingProcess.DETERMINISTIC_CAPACITY])

Process_certain_capacity = Process(name='process_certain_capacity', conversion={
                                   Resource_deterministic_demand: -0.5, Resource_deterministic_availability: -0.5, Resource_deterministic_price: -0.25, Resource_deterministic_revenue: 1},
                                   capex=100, fopex=10, vopex=1, prod_max=100, prod_min=0)
Process_storage = Process(name='process_storage', storage=Resource_deterministic_demand,
                          capex=100, fopex=5, vopex=0.5, prod_max=50, prod_min=0, store_max=25, storage_cost=0.1)

Place = Location(name='location', processes={Process_certain_capacity, Process_deterministic_capacity2, Process_deterministic_capacity, Process_storage}, scales=scales,
                 demand_scale_level=1, capacity_scale_level=1, price_scale_level=1, availability_scale_level=1,
                 demand_factor={Resource_deterministic_demand: demand_factor}, capacity_factor={Process_deterministic_capacity: capacity_factor, Process_deterministic_capacity2: capacity_factor2},
                 price_factor={Resource_deterministic_price: price_factor}, availability_factor={Resource_deterministic_availability: availability_factor},
                 revenue_factor={Resource_deterministic_revenue: revenue_factor})

Occurance = Scenario(name='scenario', scales=scales, network=Place, demand_scale_level=1, network_scale_level=0, scheduling_scale_level=1,
                     capacity_scale_level=1, purchase_scale_level=1, availability_scale_level=1,
                     demand={Place: {Resource_deterministic_demand: 25, Resource_deterministic_revenue: 25}})

# LP = formulate(scenario=Occurance, constraints={Constraints.COST, Constraints.INVENTORY,
#                Constraints.PRODUCTION, Constraints.RESOURCE_BALANCE, Constraints.DEMAND}, objective=Objective.COST)
MILP = formulate(scenario=Occurance, constraints={Constraints.COST, Constraints.NETWORK, Constraints.INVENTORY,
               Constraints.PRODUCTION, Constraints.RESOURCE_BALANCE}, objective=Objective.PROFIT)

results = solve(scenario=Occurance, instance=MILP, solver='gurobi', name='MILP')

# %%


demand_factor = pandas.DataFrame(data={'Value': [0.5, 1, 0.5, 0.25]})
capacity_factor = pandas.DataFrame(data={'Value': [1, 0.5, 1, 0.25]})
capacity_factor2 = pandas.DataFrame(data={'Value': [0.75, 1, 0.25, 0.5]})
availability_factor = pandas.DataFrame(data={'Value': [1, 1, 0.5, 0.5]})
price_factor = pandas.DataFrame(data={'Value': [0.25, 1, 0.5, 0.75]})
revenue_factor = pandas.DataFrame(data={'Value': [0.25, 1, 0.25, 0.5]})

scales = TemporalScale(discretization_list=[1, 4])

Resource_certain_availability = Resource(
    name='resource_certain_availability', cons_max=100, price=2)

Resource_deterministic_availability = Resource(name='resource_deterministic_availability', cons_max=100, price=5, varying=[
                                               VaryingResource.DETERMINISTIC_AVAILABILITY])
Resource_deterministic_demand = Resource(name='resource_deterministic_demand', demand=True, varying=[
                                         VaryingResource.DETERMINISTIC_DEMAND])
Resource_deterministic_price = Resource(name='resource_deterministic_price', cons_max=100, price=10, varying=[
                                        VaryingResource.DETERMINISTIC_PRICE])
Resource_deterministic_revenue = Resource(name='resource_deterministic_revenue', demand=True, revenue=500, varying=[
                                          VaryingResource.DETERMINISTIC_REVENUE])

Process_deterministic_capacity = Process(name='process_deterministic_capacity', conversion={Resource_certain_availability: -1, Resource_deterministic_demand: 1},
                                         capex=1000, fopex=10, vopex=1, prod_max=100, prod_min=10, varying=[VaryingProcess.DETERMINISTIC_CAPACITY])

Process_deterministic_capacity2 = Process(name='process_deterministic_capacity2', conversion={Resource_certain_availability: -1, Resource_deterministic_demand: 1},
                                         capex=2000, fopex=20, vopex=5, prod_max=100, prod_min=10, varying=[VaryingProcess.DETERMINISTIC_CAPACITY])

Process_certain_capacity = Process(name='process_certain_capacity', conversion={
                                   Resource_deterministic_demand: -0.5, Resource_deterministic_availability: -0.5, Resource_deterministic_price: -0.25, Resource_deterministic_revenue: 1},
                                   capex=100, fopex=10, vopex=1, prod_max=100, prod_min=0)
Process_storage = Process(name='process_storage', storage=Resource_deterministic_demand,
                          capex=100, fopex=5, vopex=0.5, prod_max=50, prod_min=0, store_max=25, storage_cost=0.1)

Place = Location(name='location', processes={Process_certain_capacity, Process_deterministic_capacity2, Process_deterministic_capacity, Process_storage}, scales=scales,
                 demand_scale_level=1, capacity_scale_level=1, price_scale_level=1, availability_scale_level=1,
                 demand_factor={Resource_deterministic_demand: demand_factor}, capacity_factor={Process_deterministic_capacity: capacity_factor, Process_deterministic_capacity2: capacity_factor2},
                 price_factor={Resource_deterministic_price: price_factor}, availability_factor={Resource_deterministic_availability: availability_factor},
                 revenue_factor={Resource_deterministic_revenue: revenue_factor})

Occurance = Scenario(name='scenario', scales=scales, network=Place, demand_scale_level=1, network_scale_level=0, scheduling_scale_level=1,
                     capacity_scale_level=1, purchase_scale_level=1, availability_scale_level=1,
                     demand={Place: {Resource_deterministic_demand: 25, Resource_deterministic_revenue: 25}})

# LP = formulate(scenario=Occurance, constraints={Constraints.COST, Constraints.INVENTORY,
#                Constraints.PRODUCTION, Constraints.RESOURCE_BALANCE, Constraints.DEMAND}, objective=Objective.COST)
MILP = formulate(scenario=Occurance, constraints={Constraints.COST, Constraints.NETWORK, Constraints.INVENTORY,
               Constraints.PRODUCTION, Constraints.RESOURCE_BALANCE, Constraints.DEMAND}, objective=Objective.COST)

results = solve(scenario=Occurance, instance=MILP, solver='gurobi', name='MILP')

# %%
