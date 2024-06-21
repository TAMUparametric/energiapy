from pyomo.environ import ConcreteModel, Set

from ...components.scenario import Scenario
from ...utils.scale_utils import scale_pyomo_set


def generate_transport_subsets(instance: ConcreteModel, scenario: Scenario):
    """generates transport subsets

    Args:
        instance (ConcreteModel): pyomo model
        scenario (Scenario): energiapy scenario
    """

    sets = scenario.set_dict

    instance.transports_varying_capacity = Set(
        initialize=sets['transports_varying_capacity'], doc='Set of transports with varying capacity')
    instance.transports_varying_capex = Set(
        initialize=sets['transports_varying_capex'], doc='Set of transports with varying capex')
    instance.transports_varying_fopex = Set(
        initialize=sets['transports_varying_fopex'], doc='Set of transports with varying fopex')
    instance.transports_varying_vopex = Set(
        initialize=sets['transports_varying_vopex'], doc='Set of transports with varying vopex')

    instance.transports_certain_capacity = Set(
        initialize=sets['transports_certain_capacity'], doc='Set of transports with certain capacity')
    instance.transports_certain_capex = Set(
        initialize=sets['transports_certain_capex'], doc='Set of transports with certain capex')
    instance.transports_certain_fopex = Set(
        initialize=sets['transports_certain_fopex'], doc='Set of transports with certain fopex')
    instance.transports_certain_vopex = Set(
        initialize=sets['transports_certain_vopex'], doc='Set of transports with certain vopex')

    instance.transports_uncertain_capacity = Set(
        initialize=sets['transports_uncertain_capacity'], doc='Set of transports with uncertain capacity')
    instance.transports_uncertain_capex = Set(
        initialize=sets['transports_uncertain_capex'], doc='Set of transports with uncertain capex')
    instance.transports_uncertain_fopex = Set(
        initialize=sets['transports_uncertain_fopex'], doc='Set of transports with uncertain fopex')
    instance.transports_uncertain_vopex = Set(
        initialize=sets['transports_uncertain_vopex'], doc='Set of transports with uncertain vopex')
