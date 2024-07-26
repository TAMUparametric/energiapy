from pyomo.environ import ConcreteModel, Set

from ...components.scenario import Scenario
from ...utils.scale_utils import scale_pyomo_set


def generate_temporal_sets(instance: ConcreteModel, scenario: Scenario):
    """creates temporal sets
    1. the parent set (planning horizon)
    2. scales_network
    3. scales_scheduling

    Args:
        instance (ConcreteModel): pyomo model
        scenario (Scenario): energiapy scenario
    """

    instance.scales = Set(scenario.scales.list,
                          initialize=scenario.scales.scale, doc='set of scales')

    instance.scales_network = scale_pyomo_set(
        instance=instance, scale_level=scenario.network_scale_level, doc='scale for network decisions')

    instance.scales_scheduling = scale_pyomo_set(
        instance=instance, scale_level=scenario.scheduling_scale_level, doc='scale for scheduling decisions')
