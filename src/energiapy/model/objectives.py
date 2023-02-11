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

from pyomo.environ import ConcreteModel, Objective, maximize
from ..utils.latex_utils import constraint_latex_render
from ..utils.model_utils import scale_list
from ..utils.model_utils import scale_tuple
from itertools import product


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
        capex = sum(instance.Capex_network[scale_] for scale_ in scale_iter) 
        vopex = sum(instance.Vopex_network[scale_] for scale_ in scale_iter)
        fopex = sum(instance.Fopex_network[scale_] for scale_ in scale_iter)
        incidental = sum(instance.Incidental_network[scale_] for scale_ in scale_iter)
        
        cost_purch = sum(instance.B_network[resource_, scale_] for resource_, scale_ in product(instance.resources_purch, scale_iter))
        if len(instance.locations) > 1:
            cost_trans = sum(instance.Trans_cost_network[transport_, scale_] for transport_, scale_ in product(instance.transports, scale_iter))
        else:
            cost_trans = 0
        return capex + vopex + fopex + cost_purch + cost_trans + incidental
    instance.cost_objective = Objective(rule = cost_objective_rule, doc = 'total purchase from network')
    constraint_latex_render(cost_objective_rule)
    return instance.cost_objective


def uncertainty_cost_objective(instance:ConcreteModel, penalty: float, network_scale_level:int=0, uncertainty_scale_level:int = 0) -> Objective:
    """Objective to minimize total cost

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Objective: cost objective
    """
    scale_iter = scale_tuple(instance= instance, scale_levels = network_scale_level + 1)
    scale_iter_uncertainty = scale_tuple(instance= instance, scale_levels = uncertainty_scale_level + 1)
    def uncertainty_cost_objective_rule(instance):
        capex = sum(instance.Capex_network[scale_] for scale_ in scale_iter) 
        vopex = sum(instance.Vopex_network[scale_] for scale_ in scale_iter)
        fopex = sum(instance.Fopex_network[scale_] for scale_ in scale_iter)
        cost_purch = sum(instance.B_network[resource_, scale_] for resource_, scale_ in product(instance.resources_purch, scale_iter))
        cap_penalty = penalty*sum(instance.Demand_slack[location_, scale_] for location_, scale_ in product(instance.locations, scale_iter_uncertainty)) 
        if len(instance.locations) > 1:
            cost_trans = sum(instance.Trans_cost_network[transport_, scale_] for transport_, scale_ in product(instance.transports, scale_iter))
        else:
            cost_trans = 0
        return capex + vopex + fopex + cost_purch + cost_trans + cap_penalty           
    
    instance.uncertainty_cost_objective = Objective(rule = uncertainty_cost_objective_rule, doc = 'total purchase from network')
    constraint_latex_render(uncertainty_cost_objective_rule)
    return instance.uncertainty_cost_objective

def demand_objective(instance:ConcreteModel, network_scale_level:int=0) -> Objective:
    """Objective to maximize total discharge

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Objective: cost objective
    """
    scale_iter = scale_tuple(instance= instance, scale_levels = network_scale_level + 1)
    def demand_objective_rule(instance):
        return sum(instance.S_network[resource_, scale_] for resource_, scale_ in product(instance.resources_demand, scale_iter))
    
    instance.demand_objective = Objective(rule = demand_objective_rule, doc = 'total purchase from network', sense= maximize)
    # constraint_latex_render(cost_objective_rule)
    return instance.demand_objective
