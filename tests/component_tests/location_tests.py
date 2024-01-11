from src.energiapy.components.temporal_scale import TemporalScale
from src.energiapy.components.resource import Resource, VaryingResource
from src.energiapy.components.process import Process, VaryingProcess
from src.energiapy.components.location import Location
from src.energiapy.components.scenario import Scenario
from src.energiapy.components.result import Result
from src.energiapy.model.formulate import formulate, Constraints, Objective
from src.energiapy.model.solve import solve

import pandas

demand_factor = pandas.DataFrame(data={'Value': [0.6, 0.7, 0.8, 0.3]})
capacity_factor = pandas.DataFrame(data={'Value': [0.6, 0.8, 0.9, 0.7]})
availability_factor = pandas.DataFrame(data = {'Value': [0.4, 0.9, 0.5, 0.6]})
price_factor = pandas.DataFrame(data = {'Value': [0.5, 0.6, 0.3, 0.8]})
revenue_factor = pandas.DataFrame(data= {'Value': [0.8, 0.4, 0.9, 0.6]})

scales = TemporalScale(discretization_list=[1,4])

Resource_certain_availability = Resource(name='resource_certain_availability', cons_max= 100, basis= 'Units', label = 'resource certain availability')
Resource_uncertain_availability = Resource(name='resource_uncertain_availability', cons_max= 100, basis= 'Units', label = 'resource uncertain availability', varying= [VaryingResource.DETERMINISTIC_AVAILABILITY])
Resource_uncertain_demand = Resource(name='resource_uncertain_demand', demand=True, basis= 'Units', label = 'resource uncertain demand', varying= [VaryingResource.DETERMINISTIC_DEMAND])
Resource_uncertain_price = Resource(name='resource_uncertain_price', cons_max= 100, basis= 'Units', label = 'resource uncertain price', varying = [VaryingResource.DETERMINISTIC_PRICE])
Resource_uncertain_revenue = Resource(name='resource uncertain availability', demand = True, basis='Units', label = 'resource uncertain revenue', varying = [VaryingResource.DETERMINISTIC_REVENUE])

Process_uncertain_capacity = Process(name='process_uncertain_capacity', conversion={Resource_certain_availability:-1, Resource_uncertain_demand:1}, capex= 1000, fopex=10, vopex=1, prod_max=100, prod_min=10, label='process uncertain capacity', varying=[VaryingProcess.DETERMINISTIC_CAPACITY])
Process_certain_capacity = Process(name='process_certain_capacity', conversion = {Resource_uncertain_demand:-0.6, Resource_uncertain_availability:-0.5, Resource_uncertain_price:-0.8, Resource_uncertain_revenue: 1}, capex= 100, fopex = 10, vopex= 1, label = 'process certain capacity')

location = Location(name='location', processes= {Process_certain_capacity, Process_uncertain_capacity}, scales= scales, 
                    demand_scale_level=1, capacity_scale_level=1, price_scale_level=1, availability_scale_level=1, 
                    demand_factor={Resource_uncertain_demand: demand_factor}, capacity_factor = {Process_uncertain_capacity: capacity_factor}, 
                    price_factor= {Resource_uncertain_price: price_factor}, availability_factor= {Resource_uncertain_availability},
                    revenue_factor= {Resource_uncertain_revenue: revenue_factor}, label= 'location')

Scenario(name='scenario', scales=scales, network=location, demand_scale_level=1, network_scale_level=0, scheduling_scale_level=1, demand= {location:{Resource_uncertain_demand:50, Resource_uncertain_revenue: 50}}, label = 'scenario')

lp = formulate(scenario=scenario, constraints= {Constraints.COST, Constraints.INVENTORY, Constraints.PRODUCTION, Constraints.RESOURCE_BALANCE, objective = Objective.PROFIT})

results = solve(scenario= scenario, instance= lp, solver = 'gurobi', name = 'LP')







