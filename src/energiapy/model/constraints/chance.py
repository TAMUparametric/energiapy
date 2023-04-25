"""chance constraints
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2023, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "MIT"
__version__ = "1.0.5"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from typing import Union, Dict

from pyomo.environ import ConcreteModel, Constraint

from ...utils.latex_utils import constraint_latex_render
from ...utils.scale_utils import scale_list, scale_tuple
from ...components.resource import Resource
from ...components.location import Location

def constraint_demand(instance: ConcreteModel, guarantee: float,  demand_scale_level: int = 0, scheduling_scale_level: int = 0,loc_res_dict: dict = None, ) -> Constraint:
    """Ensures that demand for resource is met at chosen temporal scale

    Args:
        instance (ConcreteModel): pyomo instance
        demand_scale_level (int, optional): scale of demand decisions. Defaults to 0.
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.
        demand_dict (dict, optional): demand at location. Defaults to {}.

    Returns:
        Constraint: demand
    """
    # scales = scale_list(instance= instance, scale_levels = demand_scale_level+1)
    scales = scale_list(instance=instance,
                        scale_levels=len(instance.scales))
    scale_iter = scale_tuple(
        instance=instance, scale_levels=scheduling_scale_level + 1)

    if loc_res_dict is None:
        loc_res_dict = dict()

    def demand_rule(instance, location, resource, *scale_list):

        if demand_factor[location] is not None:
            if isinstance(demand_factor[location][list(demand_factor[location])[0]], (float, int)):
                discharge = sum(instance.S[location, resource_, scale_list[:scheduling_scale_level + 1]] for
                                resource_ in instance.resources_demand)
            else:
                discharge = sum(instance.S[location, resource, scale_] for scale_ in scale_iter if scale_[
                    :scheduling_scale_level + 1] == scale_list)

            if isinstance(demand, dict):
                if resource in loc_res_dict[location]:
                    demandtarget = demand[location][resource] * \
                        demand_factor[location][resource][scale_list[:demand_scale_level + 1]]
                else:
                    demandtarget = 0
            else:
                if resource in loc_res_dict[location]:
                    demandtarget = demand * \
                        demand_factor[location][resource][scale_list[:demand_scale_level + 1]]
                else:
                    demandtarget = 0
        else:
            # TODO - doesn't meet demand in first timeperiod
            discharge = sum(instance.S[location, resource, scale_] for scale_ in scale_iter if scale_[
                :scheduling_scale_level + 1] == scale_list)

            if isinstance(demand, dict):
                demandtarget = demand[location][resource]
            else:
                demandtarget = demand

        return discharge >= demandtarget

    if len(instance.locations) > 1:
        instance.constraint_demand = Constraint(
            instance.sinks, instance.resources_demand, *scales, rule=demand_rule, doc='specific demand for resources')

    else:
        instance.constraint_demand = Constraint(
            instance.locations, instance.resources_demand, *scales, rule=demand_rule,
            doc='specific demand for resources')
    constraint_latex_render(demand_rule)
    return instance.constraint_demand
