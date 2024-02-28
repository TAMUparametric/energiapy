import pandas
import pytest
from src.energiapy.components.resource import Resource, VaryingResource
from src.energiapy.components.temporal_scale import TemporalScale
from src.energiapy.components.process import Process, VaryingProcess
from src.energiapy.components.location import Location
from src.energiapy.components.scenario import Scenario
from src.energiapy.components.material import Material
from src.energiapy.model.formulate import formulate, Constraints, Objective
from src.energiapy.model.solve import solve

####
@pytest.fixture()
def temporal_scale():
    """Temporal scale with 1 main period and 4 sub periods"""
    return TemporalScale(discretization_list=[1, 4])


@pytest.fixture()
def process_storage():
    """Storage process"""
    Resource1 = Resource(name='Resource1')
    return Process(name='Process1', storage=Resource1, capex=1000, fopex=100, vopex=10,
                   prod_max=100, prod_min=0.1, store_max=100, storage_loss=0.01, storage_cost=0.1)


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
                   prod_max=100, prod_min=0.1)


@pytest.fixture()
def process_multiple_modes():
    """Process with multiple modes and ramping rates"""
    prod_max = {0: 10, 1: 50}
    prod_min = {0: 0, 1: 10}
    rate_max = {0: 10, 1: 15}
    mode_ramp = {(0, 1): 0.5}
    Resource1 = Resource(name='Resource1', cons_max=1000)
    Resource2 = Resource(name='Resource2')
    return Process(name='Process1', conversion={0: {Resource1: -1, Resource2: 0.5}, 1: {Resource1: -1, Resource2: 0.75}},
                   rate_max=rate_max, mode_ramp=mode_ramp, prod_max=prod_max, prod_min=prod_min,
                   capex=1000, fopex=100, vopex=10)


@pytest.fixture()
def location_no_variability():
    """Location with no variability"""
    scales = TemporalScale(discretization_list=[1, 4])
    Resource1 = Resource(name='Resource1', cons_max=1000)
    Resource2 = Resource(name='Resource2')
    Material1 = Material(name='Material1', gwp=100)
    Material2 = Material(name='Material2', gwp=200)
    Process1 = Process(name='Process1', storage=Resource2, capex=1000, fopex=100, vopex=10,
                       prod_max=100, prod_min=0.1, store_max=100, storage_loss=0.01, storage_cost=0.1)
    Process2 = Process(name='Process2', conversion={'Mode1': {Resource1: -5, Resource2: 1}, 'Mode2': {Resource1: -10, Resource2: 1}},
                       capex={'Mode1': 2000, 'Mode2': 1000}, fopex={'Mode1': 100, 'Mode2': 200}, vopex={'Mode1': 50, 'Mode2': 10},
                       material_cons={'Mode1': {Material1: 50, Material2: 20}, 'Mode2': {
                           Material1: 100, Material2: 25}},
                       prod_max=100, prod_min=0.1)
    prod_max = {0: 10, 1: 50}
    prod_min = {0: 0, 1: 10}
    rate_max = {0: 10, 1: 15}
    mode_ramp = {(0, 1): 0.5}
    Process3 = Process(name='Process3', conversion={0: {Resource1: -1, Resource2: 0.5}, 1: {Resource1: -1, Resource2: 0.75}},
                       rate_max=rate_max, mode_ramp=mode_ramp, prod_max=prod_max, prod_min=prod_min,
                       capex=1000, fopex=100, vopex=10)
    return Location(name='Location1', processes={Process1, Process2, Process3}, scales=scales)


@pytest.fixture()
def single_location_scenario_variability():
    """Scenario with variability"""
    demand_factor = pandas.DataFrame(data={'Value': [0.6, 0.7, 0.8, 0.3]})
    capacity_factor = pandas.DataFrame(data={'Value': [0.6, 0.8, 0.9, 0.7]})
    availability_factor = pandas.DataFrame(
        data={'Value': [0.4, 0.9, 0.5, 0.6]})
    price_factor = pandas.DataFrame(data={'Value': [0.5, 0.6, 0.3, 0.8]})
    revenue_factor = pandas.DataFrame(data={'Value': [0.8, 0.4, 0.9, 0.6]})

    scales = TemporalScale(discretization_list=[1, 4])

    Resource_certain_availability = Resource(
        name='resource_certain_availability', cons_max=100)

    Resource_deterministic_availability = Resource(name='resource_deterministic_availability', cons_max=100, varying=[
                                                   VaryingResource.DETERMINISTIC_AVAILABILITY])
    Resource_deterministic_demand = Resource(name='resource_deterministic_demand', demand=True, revenue=5, varying=[
                                             VaryingResource.DETERMINISTIC_DEMAND])
    Resource_deterministic_price = Resource(name='resource_deterministic_price', cons_max=100, price=10, varying=[
                                            VaryingResource.DETERMINISTIC_PRICE])
    Resource_deterministic_revenue = Resource(name='resource_deterministic_revenue', revenue=20, demand=True, varying=[
                                              VaryingResource.DETERMINISTIC_REVENUE])

    Process_deterministic_capacity = Process(name='process_deterministic_capacity', conversion={Resource_certain_availability: -1, Resource_deterministic_demand: 1},
                                             capex=1000, fopex=10, vopex=1, prod_max=100, prod_min=10, varying=[VaryingProcess.DETERMINISTIC_CAPACITY])
    Process_certain_capacity = Process(name='process_certain_capacity', conversion={
        Resource_deterministic_demand: -0.6, Resource_deterministic_availability: -0.5, Resource_deterministic_price: -0.8, Resource_deterministic_revenue: 1},
        capex=100, fopex=10, vopex=1)

    Location1 = Location(name='location', processes={Process_certain_capacity, Process_deterministic_capacity}, scales=scales,
                         demand_scale_level=1, capacity_scale_level=1, price_scale_level=1, availability_scale_level=1,
                         demand_factor={Resource_deterministic_demand: demand_factor}, capacity_factor={Process_deterministic_capacity: capacity_factor},
                         price_factor={Resource_deterministic_price: price_factor}, availability_factor={Resource_deterministic_availability: availability_factor},
                         revenue_factor={Resource_deterministic_revenue: revenue_factor})

    return Scenario(name='scenario', scales=scales, network=Location1, demand_scale_level=1, network_scale_level=0, scheduling_scale_level=1,
                    capacity_scale_level=1, purchase_scale_level=1, availability_scale_level=1,
                    demand={Location1: {Resource_deterministic_demand: 25, Resource_deterministic_revenue: 25}})
