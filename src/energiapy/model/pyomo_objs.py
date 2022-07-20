"""pyomo objective
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "0.0.1"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from pyomo.environ import ConcreteModel, Objective 
from ..utils.latex_utils import constraint_latex_render
from ..utils.model_utils import scale_list
from ..utils.model_utils import scale_tuple


def cost_objective(instance:ConcreteModel, network_scale_level:int=0) -> Objective:
    """Objective to minimize total cost

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Objective: cost objective
    """
    scale_iter = scale_tuple(instance= instance, scale_levels = network_scale_level + 1)
    def cost_objective_rule(instance):
        return sum(instance.Capex_network[scale_] + instance.Vopex_network[scale_] + instance.Fopex_network[scale_] \
            + sum(instance.B_network[resource_, scale_] for resource_ in instance.resources_purch) for scale_ in scale_iter) 
    instance.cost_objective = Objective(rule = cost_objective_rule, doc = 'total purchase from network')
    constraint_latex_render(cost_objective_rule)
    return instance.cost_objective