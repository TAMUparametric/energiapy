from pyomo.environ import ConcreteModel, Set

from ...components.scenario import Scenario
from ...utils.scale_utils import scale_pyomo_set


def generate_location_subsets(instance: ConcreteModel, scenario: Scenario):
    """generates location subsets

    Args:
        instance (ConcreteModel): pyomo model
        scenario (Scenario): energiapy scenario
    """

    sets = scenario.set_dict

    if scenario.sources is not None:
        instance.sources = Set(
            initialize=sets['sources'], doc='Set of sources')

    if scenario.sinks is not None:
        instance.sinks = Set(initialize=sets['sinks'], doc='Set of sinks')
