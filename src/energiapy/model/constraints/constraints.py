"""Available b_traints
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "MIT"
__version__ = "1.0.5"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from enum import Enum, auto
from typing import Union, Dict, Tuple

from pyomo.environ import ConcreteModel, Constraint, Var, Set

# from ...utils.latex_utils import co_traint_latex_render
from ...utils.scale_utils import scale_list, scale_tuple
from ...components.resource import Resource
from ...components.location import Location
from ...components.process import Process


class Cons(Enum):
    X_LEQ_B = auto()
    X_EQ_B = auto()
    X_GEQ_B = auto()
    X_LEQ_BY = auto()
    X_EQ_BY = auto()
    X_GEQ_BY = auto()
    X_LEQ_Y = auto()
    X_EQ_Y = auto()
    X_GEQ_Y = auto()
    X_EQ_SUMSCALE_Y = auto()
    X_EQ_SUMLOC_Y = auto()
    X_EQ_CY = auto()
    X_EQ_C = auto()


def make_constraint(instance: ConcreteModel, type_cons: Cons, variable_x: Var, location_set: Set, component_set: Set, b_max: dict = None,  loc_comp_dict: dict = None,
                    b_factor: dict = None, x_scale_level: int = 0, b_scale_level: int = 0, y_scale_level: int = 0, variable_y: Var = None, label: str = None,
                    c_component: dict = None, c_factor: dict = None, c_scale_level: int = 0, cluster_wt: dict = None) -> Constraint:

    if type_cons in [Cons.X_EQ_SUMLOC_Y, Cons.X_EQ_SUMSCALE_Y]:
        scales = scale_list(instance=instance,
                            scale_levels=x_scale_level + 1)
        scale_iter = scale_tuple(
            instance=instance, scale_levels=y_scale_level+1)
    else:
        scales = scale_list(instance=instance,
                            scale_levels=max(x_scale_level, y_scale_level, b_scale_level) + 1)

    def cons_rule(instance, location, component, *scale):
        x = getattr(instance, variable_x)[
            location, component, scale[:x_scale_level + 1]]

        def weight(x): return 1 if cluster_wt is None else cluster_wt[x]

        if b_max is not None:
            if isinstance(b_max[location][component], dict) is True:
                bmax = b_max[location][component][list(
                    b_max[location][component].keys())[-1:][0]]
            else:
                bmax = b_max[location][component]

        else:
            bmax = 1

        if c_component is not None:
            c = c_component[component]
            if c_factor[location] is not None:
                c = c_factor[location][component][scale[:c_scale_level + 1]
                                                  ]*c_component[component]

        if b_factor is not None:
            if b_factor[location] is not None:
                bfactor = b_factor[location][component][scale[:b_scale_level + 1]
                                                        ]
            else:
                bfactor = 1
        else:
            bfactor = 1

        b = bmax*bfactor

        if variable_y is not None:

            if type_cons == Cons.X_EQ_SUMSCALE_Y:
                d_sum = sum(weight(scale_)*getattr(instance, variable_y)[location, component, scale_[
                            :y_scale_level + 1]] for scale_ in scale_iter if scale_[:x_scale_level + 1] == scale)
                print(d_sum)
            else:
                y = getattr(instance, variable_y)[
                    location, component, scale[:y_scale_level + 1]]

        if loc_comp_dict[location] is not None:
            if component in loc_comp_dict[location]:
                if type_cons == Cons.X_LEQ_B:

                    return x <= b
                if type_cons == Cons.X_EQ_B:
                    return x == b
                if type_cons == Cons.X_GEQ_B:
                    return x >= b
                if type_cons == Cons.X_LEQ_BY:
                    return x <= b*y
                if type_cons == Cons.X_EQ_BY:
                    return x == b*y
                if type_cons == Cons.X_GEQ_BY:
                    return x >= b*y
                if type_cons == Cons.X_LEQ_Y:
                    return x <= y
                if type_cons == Cons.X_EQ_Y:
                    return x == y
                if type_cons == Cons.X_GEQ_Y:
                    return x >= y
                if type_cons == Cons.X_EQ_CY:
                    return x == c*y
                if type_cons == Cons.X_EQ_C:
                    return x == c
                if type_cons in [Cons.X_EQ_SUMLOC_Y, Cons.X_EQ_SUMSCALE_Y]:
                    print('d')
                    return x == d_sum
            else:
                return x == 0

    # print(f'{variable_x} <= {variable_x}MAX')
    return Constraint(location_set, component_set, *scales, rule=cons_rule, doc=label)


# def make_sum_constraint()
# def constraint_location_production(instance: ConcreteModel, cluster_wt: dict,
#                                    network_scale_level: int = 0, scheduling_scale_level: int = 0) -> Constraint:
#     """Determines total production capacity utilization at location

#     Args:
#         instance (ConcreteModel): pyomo instance
#         network_scale_level (int, optional): scale of network decisions. Defaults to 0.
#         scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.
#     Returns:
#         Constraint: location_production
#     """

#     scales = scale_list(instance=instance,
#                         scale_levels=network_scale_level + 1)
#     scale_iter = scale_tuple(
#         instance=instance, scale_levels=scheduling_scale_level+1)

#     def location_production_rule(instance, location, process, *scale_list):
#         def weight(x): return 1 if cluster_wt is None else cluster_wt[x]
#         return instance.P_location[location, process, scale_list] == sum(
#             weight(scale_) * instance.P[location, process, scale_[:scheduling_scale_level + 1]] for scale_ in scale_iter if scale_[:network_scale_level + 1] == scale_list)

#     instance.constraint_location_production = Constraint(
#         instance.locations, instance.processes, *scales, rule=location_production_rule,
#         doc='total production at location')
#     constraint_latex_render(location_production_rule)
#     return instance.constraint_location_production


class Constraints(Enum):
    """Class of Constraints
    """
    COST = auto()
    EMISSION = auto()
    FAILURE = auto()
    INVENTORY = auto()
    LAND = auto()
    PRODUCTION = auto()
    RESOURCE_BALANCE = auto()
    TRANSPORT = auto()
    UNCERTAIN = auto()
    MODE = auto()
    LIFECYCLE = auto()
    NETWORK = auto()
    CREDIT = auto()
    MATERIAL = auto()
    PRESERVE_NETWORK = auto()
    DEMAND = auto()
