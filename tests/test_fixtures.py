import pandas
import pytest
from src.energiapy.components.resource import Resource, VaryingResource
from src.energiapy.components.temporal_scale import TemporalScale
from src.energiapy.components.process import Process, VaryingProcess
from src.energiapy.components.location import Location
from src.energiapy.components.scenario import Scenario
from src.energiapy.model.formulate import formulate, Constraints, Objective
from src.energiapy.model.solve import solve


@pytest.fixture()
def temporal_scale():
    """Test temporal scale with 1 main period and 4 sub periods"""
    return TemporalScale(discretization_list=[1, 4])


@pytest.fixture

# @pytest.fixture()
# def resource_deterministic_availability():
#     """Consumable resource with deterministic availability"""
#     cons_max = 100
#     return Resource(name='resource_deterministic_availability', cons_max=cons_max, basis='Units',
#                     label='resource deterministic availability', varying=[VaryingResource.DETERMINISTIC_AVAILABILITY])


# @pytest.fixture()
# def resource_deterministic_demand():
#     """Dischargeable resource with deterministic demand"""
#     return Resource(name='resource_deterministic_demand', demand=True, basis='Units',
#                     label='resource deterministic demand', varying=[VaryingResource.DETERMINISTIC_DEMAND])


# @pytest.fixture()
# def resource_deterministic_price():
#     """Consumable resource with deterministic selling price"""
#     cons_max = 100
#     return Resource(name='resource_deterministic_price', cons_max=cons_max, basis='Units',
#                     label='resource deterministic price', varying=[VaryingResource.DETERMINISTIC_PRICE])


# @pytest.fixture()
# def resource_deterministic_revenue():
#     """Dischargeable resource with deterministic revenue"""
#     return Resource(name='resource deterministic availability', demand=True, basis='Units',
#                     label='resource deterministic revenue', varying=[VaryingResource.DETERMINISTIC_REVENUE])


# @pytest.fixture()
# def process_deterministic_capacity():
#     """Process with deterministic capacity"""
#     Resource_certain_availability = Resource(
#         name='resource_certain_availability', cons_max=100, basis='Units', label='resource certain availability')
#     Resource_deterministic_demand = Resource(name='resource_deterministic_demand', demand=True, basis='Units',
#                                          label='resource deterministic demand', varying=[VaryingResource.DETERMINISTIC_DEMAND])
#     return Process(name='process_deterministic_capacity', conversion={Resource_certain_availability: -1, Resource_deterministic_demand: 1},
#                    capex=1000, fopex=10, vopex=1, prod_max=100, prod_min=10, label='process deterministic capacity', varying=[VaryingProcess.DETERMINISTIC_CAPACITY])


# @pytest.fixture()
# def process_certain_capacity():
#     """Process with certain capacity"""
    
#     Resource_deterministic_availability = Resource(name='resource_deterministic_availability', cons_max=100, basis='Units',
#                                            label='resource deterministic availability', varying=[VaryingResource.DETERMINISTIC_AVAILABILITY])
#     Resource_deterministic_demand = Resource(name='resource_deterministic_demand', demand=True, basis='Units',
#                                          label='resource deterministic demand', varying=[VaryingResource.DETERMINISTIC_DEMAND])
#     Resource_deterministic_price = Resource(name='resource_deterministic_price', cons_max=100, basis='Units',
#                                         label='resource deterministic price', varying=[VaryingResource.DETERMINISTIC_PRICE])
#     Resource_deterministic_revenue = Resource(name='resource deterministic availability', demand=True, basis='Units',
#                                           label='resource deterministic revenue', varying=[VaryingResource.DETERMINISTIC_REVENUE])
#     return Process(name='process_certain_capacity', conversion={
#         Resource_deterministic_demand: -0.6, Resource_deterministic_availability: -0.5, Resource_deterministic_price: -0.8, Resource_deterministic_revenue: 1},
#         capex=100, fopex=10, vopex=1, label='process certain capacity')


