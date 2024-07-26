"""chance constraints
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2023, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "MIT"
__version__ = "2.0.0"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from pyomo.environ import ConcreteModel, Constraint

from ...utils.math_utils import norm_constant
from ...utils.scale_utils import scale_list


def chance_normal(instance: ConcreteModel, a: str, b: float, b_factor: dict, mean: float, sd: float, compliance_list: list,  alpha: float, sign: str) -> Constraint:
    """Generates a chance constraint for normal distribution 

    Args:
        instance (ConcreteModel): pyomo instance
        a (str): variable 
        b (float): maximum b
        b_factor (dict): dictionary with varying b temporal data
        mean (float): mean
        sd (float): standard deviation
        compliance_list (list): discretization to sample normal distribution at
        alpha (float): level of compliance
        sign (str): 'leq', 'eq', 'geq'

    Returns:
        Constraint: chance constraint for normal demand of the form: a < b*b_factor*(mean - (1 - alpha*complaince[alpha])*sd)
    """
    c_dict = {p: norm_constant(p, mean, sd) for p in compliance_list}
    scales = scale_list(instance=instance,
                        scale_levels=2)

    def chance_rule(instance, location, resource, *scales):
        lhs = getattr(instance, a)[location, resource, scales]
        rhs = b*b_factor[scales]*(mean - (1 - alpha*c_dict[alpha])*sd)
        # rhs = mean - c_dict[alpha]*sd
        if sign == 'leq':
            return lhs <= rhs
        if sign == 'eq':
            return lhs == rhs
        if sign == 'geq':
            return lhs >= rhs
    return Constraint(instance.locations, instance.resources_demand, *scales, rule=chance_rule)
