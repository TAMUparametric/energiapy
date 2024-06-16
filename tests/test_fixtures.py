import pandas
import pytest
from src.energiapy.components.resource import Resource, VaryingResource
from src.energiapy.components.temporal_scale import TemporalScale
from src.energiapy.components.process import Process, VaryingProcess
from src.energiapy.components.location import Location
from src.energiapy.components.scenario import Scenario
from src.energiapy.components.material import Material
from src.energiapy.components.transport import Transport
from src.energiapy.components.network import Network
from src.energiapy.components.case_study import CaseStudy
from src.energiapy.model.formulate import formulate, Constraints, Objective
from src.energiapy.model.solve import solve


@pytest.fixture()
def temporal_scale():
    """Temporal scale with 1 main period and 4 sub periods"""
    return TemporalScale(discretization_list=[1, 4])


@pytest.fixture()
def process_storage():
    """Storage process"""
    Resource1 = Resource(name='Resource1')
    return Process(name='Process1', storage=Resource1, capex=1000, fopex=100, vopex=10,
                   cap_max=100, cap_min=0.1, store_max=100, storage_loss=0.01, storage_cost=0.1)


@pytest.fixture()
def process_material_modes():
    """Process with material modes"""
    Resource1 = Resource(name='Resource1', cons_max=1000)
    Resource2 = Resource(name='Resource2')
    Material1 = Material(name='Material1', gwp=100)
    Material2 = Material(name='Material2', gwp=200)
    return Process(name='Process1', conversion={'Mode1': {Resource1: -5, Resource2: 1}, 'Mode2': {Resource1: -10, Resource2: 1}},
                   capex={'Mode1': 2000, 'Mode2': 1000}, fopex={'Mode1': 100, 'Mode2': 200}, vopex={'Mode1': 50, 'Mode2': 10},
                   material_cons={'Mode1': {Material1: 50, Material2: 20}, 'Mode2': {
                       Material1: 100, Material2: 25}},
                   cap_max=100, cap_min=0.1)


# @pytest.fixture()
# def process_multiple_modes():
#     """Process with multiple modes and ramping rates"""
#     cap_max = {0: 10, 1: 50}
#     cap_min = {0: 0, 1: 10}
#     rate_max = {0: 10, 1: 15}
#     mode_ramp = {(0, 1): 0.5}
#     Resource1 = Resource(name='Resource1', cons_max=1000)
#     Resource2 = Resource(name='Resource2')
#     return Process(name='Process1', conversion={0: {Resource1: -1, Resource2: 0.5}, 1: {Resource1: -1, Resource2: 0.75}},
#                    rate_max=rate_max, mode_ramp=mode_ramp, cap_max=cap_max, cap_min=cap_min,
#                    capex=1000, fopex=100, vopex=10)


@pytest.fixture()
def location_no_variability():
    """Location with no variability"""
    scales = TemporalScale(discretization_list=[1, 4])
    Resource1 = Resource(name='Resource1', cons_max=1000)
    Resource2 = Resource(name='Resource2')
    Material1 = Material(name='Material1', gwp=100)
    Material2 = Material(name='Material2', gwp=200)
    Process1 = Process(name='Process1', storage=Resource2, capex=1000, fopex=100, vopex=10,
                       cap_max=100, cap_min=0.1, store_max=100, storage_loss=0.01, storage_cost=0.1)
    Process2 = Process(name='Process2', conversion={'Mode1': {Resource1: -5, Resource2: 1}, 'Mode2': {Resource1: -10, Resource2: 1}},
                       capex={'Mode1': 2000, 'Mode2': 1000}, fopex={'Mode1': 100, 'Mode2': 200}, vopex={'Mode1': 50, 'Mode2': 10},
                       material_cons={'Mode1': {Material1: 50, Material2: 20}, 'Mode2': {
                           Material1: 100, Material2: 25}},
                       cap_max=100, cap_min=0.1)
    cap_max = {0: 10, 1: 50}
    cap_min = {0: 0, 1: 10}
    rate_max = {0: 10, 1: 15}
    mode_ramp = {(0, 1): 0.5}
    Process3 = Process(name='Process3', conversion={0: {Resource1: -1, Resource2: 0.5}, 1: {Resource1: -1, Resource2: 0.75}},
                       rate_max=rate_max, mode_ramp=mode_ramp, cap_max=cap_max, cap_min=cap_min,
                       capex=1000, fopex=100, vopex=10)
    return Location(name='Location1', processes={Process1, Process2, Process3}, scales=scales)


@pytest.fixture()
def single_location_scenario_variability():
    """Scenario with variability"""
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
    Resource_deterministic_revenue = Resource(name='resource_deterministic_revenue', demand=True, revenue=20, varying=[
        VaryingResource.DETERMINISTIC_REVENUE])

    Process_deterministic_capacity = Process(name='process_deterministic_capacity', conversion={Resource_certain_availability: -1, Resource_deterministic_demand: 1},
                                             capex=1000, fopex=10, vopex=1, cap_max=100, cap_min=0, varying=[VaryingProcess.DETERMINISTIC_CAPACITY])
    Process_certain_capacity = Process(name='process_certain_capacity', conversion={
        Resource_deterministic_demand: -0.5, Resource_deterministic_availability: -0.5, Resource_deterministic_price: -0.25, Resource_deterministic_revenue: 1},
        capex=100, fopex=10, vopex=1, cap_max=100, cap_min=0)
    Process_storage = Process(name='process_storage', storage=Resource_deterministic_demand,
                              capex=100, fopex=5, vopex=0.5, cap_max=50, cap_min=0, store_max=25, storage_cost=0.1)

    Location1 = Location(name='location', processes={Process_certain_capacity, Process_deterministic_capacity, Process_storage}, scales=scales,
                         demand_factor_scale_level=1, capacity_factor_scale_level=1, price_factor_scale_level=1, availability_factor_scale_level=1, revenue_factor_scale_level=1,
                         demand_factor={Resource_deterministic_demand: demand_factor}, capacity_factor={Process_deterministic_capacity: capacity_factor},
                         price_factor={Resource_deterministic_price: price_factor}, availability_factor={Resource_deterministic_availability: availability_factor},
                         revenue_factor={Resource_deterministic_revenue: revenue_factor})

    return Scenario(name='scenario', scales=scales, network=Location1, demand_scale_level=1, network_scale_level=0, scheduling_scale_level=1,
                    demand={Location1: {Resource_deterministic_demand: 25, Resource_deterministic_revenue: 25}})


@pytest.fixture()
def single_location_lp_variability_cost():
    """LP for scenario with variability"""
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
                                             capex=1000, fopex=10, vopex=1, cap_max=100, cap_min=0, varying=[VaryingProcess.DETERMINISTIC_CAPACITY])
    Process_certain_capacity = Process(name='process_certain_capacity', conversion={
        Resource_deterministic_demand: -0.5, Resource_deterministic_availability: -0.5, Resource_deterministic_price: -0.25, Resource_deterministic_revenue: 1},
        capex=100, fopex=10, vopex=1, cap_max=100, cap_min=0)
    Process_storage = Process(name='process_storage', storage=Resource_deterministic_demand,
                              capex=100, fopex=5, vopex=0.5, cap_max=50, cap_min=0, store_max=25, storage_cost=0.1)

    Location1 = Location(name='location', processes={Process_certain_capacity, Process_deterministic_capacity, Process_storage}, scales=scales,
                         demand_factor_scale_level=1, capacity_factor_scale_level=1, price_factor_scale_level=1, availability_factor_scale_level=1, revenue_factor_scale_level=1,
                         demand_factor={Resource_deterministic_demand: demand_factor}, capacity_factor={Process_deterministic_capacity: capacity_factor},
                         price_factor={Resource_deterministic_price: price_factor}, availability_factor={Resource_deterministic_availability: availability_factor},
                         revenue_factor={Resource_deterministic_revenue: revenue_factor})

    Scenario1 = Scenario(name='scenario', scales=scales, network=Location1, demand_scale_level=1, network_scale_level=0, scheduling_scale_level=1,
                         demand={Location1: {Resource_deterministic_demand: 25, Resource_deterministic_revenue: 25}})

    return formulate(scenario=Scenario1, constraints={Constraints.COST, Constraints.INVENTORY,
                                                      Constraints.PRODUCTION, Constraints.RESOURCE_BALANCE, Constraints.DEMAND}, objective=Objective.COST)


@pytest.fixture()
def single_location_lp_variability_profit():
    """LP for scenario with variability"""
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
                                             capex=1000, fopex=10, vopex=1, cap_max=100, cap_min=0, varying=[VaryingProcess.DETERMINISTIC_CAPACITY])
    Process_certain_capacity = Process(name='process_certain_capacity', conversion={
        Resource_deterministic_demand: -0.5, Resource_deterministic_availability: -0.5, Resource_deterministic_price: -0.25, Resource_deterministic_revenue: 1},
        capex=100, fopex=10, vopex=1, cap_max=100, cap_min=0)
    Process_storage = Process(name='process_storage', storage=Resource_deterministic_demand,
                              capex=100, fopex=5, vopex=0.5, cap_max=50, cap_min=0, store_max=25, storage_cost=0.1)

    Location1 = Location(name='location', processes={Process_certain_capacity, Process_deterministic_capacity, Process_storage}, scales=scales,
                         demand_factor_scale_level=1, capacity_factor_scale_level=1, price_factor_scale_level=1, availability_factor_scale_level=1, revenue_factor_scale_level=1,
                         demand_factor={Resource_deterministic_demand: demand_factor}, capacity_factor={Process_deterministic_capacity: capacity_factor},
                         price_factor={Resource_deterministic_price: price_factor}, availability_factor={Resource_deterministic_availability: availability_factor},
                         revenue_factor={Resource_deterministic_revenue: revenue_factor})

    Scenario1 = Scenario(name='scenario', scales=scales, network=Location1, demand_scale_level=1, network_scale_level=0, scheduling_scale_level=1,
                         demand={Location1: {Resource_deterministic_demand: 25, Resource_deterministic_revenue: 25}})

    return formulate(scenario=Scenario1, constraints={Constraints.COST, Constraints.INVENTORY,
                                                      Constraints.PRODUCTION, Constraints.RESOURCE_BALANCE}, objective=Objective.PROFIT)


@pytest.fixture()
def single_location_milp_variability_cost():
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
                                             capex=1000, fopex=10, vopex=1, cap_max=100, cap_min=10, varying=[VaryingProcess.DETERMINISTIC_CAPACITY])

    Process_deterministic_capacity2 = Process(name='process_deterministic_capacity2', conversion={Resource_certain_availability: -1, Resource_deterministic_demand: 1},
                                              capex=2000, fopex=20, vopex=5, cap_max=100, cap_min=10, varying=[VaryingProcess.DETERMINISTIC_CAPACITY])

    Process_certain_capacity = Process(name='process_certain_capacity', conversion={
        Resource_deterministic_demand: -0.5, Resource_deterministic_availability: -0.5, Resource_deterministic_price: -0.25, Resource_deterministic_revenue: 1},
        capex=100, fopex=10, vopex=1, cap_max=100, cap_min=0)
    Process_storage = Process(name='process_storage', storage=Resource_deterministic_demand,
                              capex=100, fopex=5, vopex=0.5, cap_max=50, cap_min=0, store_max=25, storage_cost=0.1)

    Location1 = Location(name='location', processes={Process_certain_capacity, Process_deterministic_capacity2, Process_deterministic_capacity, Process_storage}, scales=scales,
                         demand_factor_scale_level=1, capacity_factor_scale_level=1, price_factor_scale_level=1, availability_factor_scale_level=1, revenue_factor_scale_level=1,
                         demand_factor={Resource_deterministic_demand: demand_factor}, capacity_factor={Process_deterministic_capacity: capacity_factor, Process_deterministic_capacity2: capacity_factor2},
                         price_factor={Resource_deterministic_price: price_factor}, availability_factor={Resource_deterministic_availability: availability_factor},
                         revenue_factor={Resource_deterministic_revenue: revenue_factor})

    Scenario1 = Scenario(name='scenario', scales=scales, network=Location1, demand_scale_level=1, network_scale_level=0, scheduling_scale_level=1,
                         demand={Location1: {Resource_deterministic_demand: 25, Resource_deterministic_revenue: 25}})

    return Scenario1, formulate(scenario=Scenario1, constraints={Constraints.COST, Constraints.NETWORK, Constraints.INVENTORY,
                                                                 Constraints.PRODUCTION, Constraints.RESOURCE_BALANCE, Constraints.DEMAND}, objective=Objective.COST)


@pytest.fixture()
def multi_location_milp_variability_cost():
    capacity_factor = pandas.DataFrame(data=[0.5, 0.75, 1, 0.5])
    price_factor = pandas.DataFrame(data=[0.75, 0.8, 0.25, 1.0])
    demand_factor = pandas.DataFrame(data=[0.6, 0.8, 0.4, 1.0])

    scales = TemporalScale(discretization_list=[1, 4])

    resource_certain_availability = Resource(
        name='resource_certain_availability', cons_max=100)

    resource_implicit = Resource(name='resource_implicit')

    resource_implicit2 = Resource(name='resource_implicit2')

    resource_deterministic_demand = Resource(
        name='resource_deterministic_demand', demand=True, revenue=2000)

    resource_deterministic_price = Resource(name='resource_deterministic_price', cons_max=100, price=3.00, varying=[
                                            VaryingResource.DETERMINISTIC_PRICE])

    resource_sell = Resource(name='resource_sell', sell=True)

    process_deterministic_capacity = Process(name='process_deterministic_capacity', conversion={resource_certain_availability: -1.25, resource_implicit: 1},
                                             capex=100, fopex=10, vopex=1, cap_max=100, varying=[VaryingProcess.UNCERTAIN_CAPACITY])

    process_certain_capacity = Process(name='process_certain_capacity', conversion={resource_implicit: -0.5, resource_deterministic_price: -0.75, resource_implicit2: 1},
                                       capex=200, fopex=25, vopex=5, cap_max=100)

    process_certain_capacity2 = Process(name='process_certain_capacity2', conversion={resource_implicit2: -1, resource_deterministic_demand: 1},
                                        capex=10, fopex=1, vopex=0.1, cap_max=100)

    location1 = Location(name='location1', processes={process_deterministic_capacity}, capacity_factor={process_deterministic_capacity: capacity_factor},
                         scales=scales, capacity_factor_scale_level=1)

    location2 = Location(name='location2', processes={process_certain_capacity}, price_factor={resource_deterministic_price: price_factor},
                         scales=scales, price_factor_scale_level=1)

    location3 = Location(name='location3', processes={process_certain_capacity2}, demand_factor={resource_deterministic_demand: demand_factor}, scales=scales,
                         demand_factor_scale_level=1)
    transport = Transport(name='transport', resources={
                          resource_implicit}, trans_max=100, trans_loss=0.1, capex=40, vopex=1)
    transport2 = Transport(name='transport2', resources={
                           resource_implicit2}, trans_max=100, trans_loss=0.05, capex=20, vopex=5)

    distance_matrix = [
        [10, 0],
        [0, 50],
    ]

    transport_matrix = [
        [[transport], []],
        [[], [transport2]],
    ]

    network = Network(name='network', source_locations=[location1, location2], sink_locations=[location2, location3],
                      distance_matrix=distance_matrix, transport_matrix=transport_matrix, scales=scales)

    scenario = Scenario(name='scenario', network=network, scales=scales, scheduling_scale_level=1,
                        network_scale_level=0, demand_scale_level=1, demand={l: {resource_deterministic_demand: 50} if l == location3 else {resource_deterministic_demand: 0} for l in network.locations})
    casestudy = CaseStudy(name='casestudy', scenarios=[scenario])

    casestudy.formulate(constraints={Constraints.COST, Constraints.INVENTORY, Constraints.PRODUCTION,
                        Constraints.RESOURCE_BALANCE, Constraints.NETWORK, Constraints.DEMAND, Constraints.TRANSPORT}, objective=Objective.COST)
    return casestudy
