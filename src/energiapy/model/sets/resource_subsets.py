from pyomo.environ import ConcreteModel, Set

from ...components.scenario import Scenario
from ...utils.scale_utils import scale_pyomo_set


def generate_resource_subsets(instance: ConcreteModel, scenario: Scenario):
    """generates resource subsets

    Args:
        instance (ConcreteModel): pyomo model
        scenario (Scenario): energiapy scenario
    """

    sets = scenario.set_dict

    instance.resources_sell = Set(
        initialize=sets['resources_sell'], doc='Set of dischargeable resources')
    instance.resources_store = Set(
        initialize=sets['resources_store'], doc='Set of storeable resources')
    instance.resources_purch = Set(
        initialize=sets['resources_purch'], doc='Set of purchased resources')

    instance.resources_varying_price = Set(initialize=sets['resources_varying_price'],
                                           doc='Set of resources with varying purchase price')

    instance.resources_certain_price = Set(initialize=sets['resources_certain_price'],
                                           doc='Set of resources with certain purchase price')

    instance.resources_varying_availability = Set(initialize=sets['resources_varying_availability'],
                                                  doc='Set of resources with varying purchase price')

    instance.resources_certain_availability = Set(initialize=sets['resources_certain_availability'],
                                                  doc='Set of resources with certain purchase price')

    instance.resources_varying_revenue = Set(initialize=sets['resources_varying_revenue'],
                                             doc='Set of resources with varying selling revenue')
    instance.resources_certain_revenue = Set(initialize=sets['resources_certain_revenue'],
                                             doc='Set of resources with certain selling revenue')
    instance.resources_varying_demand = Set(initialize=sets['resources_varying_demand'],
                                            doc='Set of resources with varying purchase price')
    instance.resources_certain_demand = Set(initialize=sets['resources_certain_demand'],
                                            doc='Set of resources with certain purchase price')
    instance.resources_demand = Set(
        initialize=sets['resources_demand'], doc='Set of resources with exact demand')

    if scenario.transports is not None:
        instance.resources_trans = Set(
            initialize=sets['resources_trans'], doc='Set of transportable resources')

    instance.resources_uncertain_price = Set(initialize=sets['resources_uncertain_price'],
                                             doc='Set of resources with uncertain purchase price')
    instance.resources_uncertain_revenue = Set(initialize=sets['resources_uncertain_revenue'],
                                               doc='Set of resources with uncertain purchase revenue')

    instance.resources_uncertain_demand = Set(initialize=sets['resources_uncertain_demand'],
                                              doc='Set of resources with uncertain demand')
