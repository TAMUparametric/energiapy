"""emission constraints
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2023, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "MIT"
__version__ = "1.0.5"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from pyomo.environ import ConcreteModel, Constraint

from ...utils.latex_utils import constraint_latex_render



def constraint_global_warming_emissions_constant_total(instance: ConcreteModel, resource_gwp_network_constant_dict: dict) -> Constraint:
    """Global warming potential for the whole network

    Args:
        instance (ConcreteModel): pyomo model instance
        network_scale_level (int, optional): scale for network decisions. Defaults to 0.

    Returns:
        Constraint: global_warming_emissions_network
    """

    # def global_warming_emissions_constant_total_rule(instance):
    #     return instance.global_warming_emissions_constant_total == sum((instance.S_network[resource, scale_] + instance.C_network[resource, scale_]) * resource_gwp_network_constant_dict[resource][scale_] for resource in instance.resources for scale_ in instance.scales_network)
    # instance.constraint_global_warming_emissions_constant_total = Constraint(rule=global_warming_emissions_constant_total_rule, doc='global warming emissions for the whole network')
    # constraint_latex_render(global_warming_emissions_constant_total_rule)
    # return instance.constraint_global_warming_emissions_constant_total

    def global_warming_emissions_constant_total_rule(instance):
        return instance.global_warming_emissions_constant_total == sum(instance.S_network[resource, scale_] * resource_gwp_network_constant_dict[resource][(scale_,)] for resource in instance.resources_sell for scale_ in instance.scales_network) + sum(instance.C_network[resource, scale_] * resource_gwp_network_constant_dict[resource][(scale_,)] for resource in instance.resources_purch for scale_ in instance.scales_network)
    instance.constraint_global_warming_emissions_constant_total = Constraint(
        rule=global_warming_emissions_constant_total_rule, doc='global warming emissions for the whole network')
    constraint_latex_render(global_warming_emissions_constant_total_rule)
    return instance.constraint_global_warming_emissions_constant_total
