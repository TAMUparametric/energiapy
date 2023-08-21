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
    X_EQ_SUM_Y = auto()
    X_EQ_CY = auto()
    X_EQ_C = auto()


def make_constraint(instance: ConcreteModel, type_cons: Cons, variable_x: Var, location_set: Set, component_set: Set, b_max: dict = None,  loc_comp_dict: dict = None,
                    b_factor: dict = None, x_scale_level: int = 0, b_scale_level: int = 0, y_scale_level: int = 0, variable_y: Var = None, label: str = None, c_component: dict = None, c_factor: dict = None, c_scale_level: int = 0) -> Constraint:

    scales = scale_list(instance=instance,
                        scale_levels=max(x_scale_level, y_scale_level, b_scale_level) + 1)

    def cons_rule(instance, location, component, *scale):
        x = getattr(instance, variable_x)[
            location, component, scale[:x_scale_level + 1]]

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
            else:
                return x == 0

    # print(f'{variable_x} <= {variable_x}MAX')
    return Constraint(location_set, component_set, *scales, rule=cons_rule, doc=label)


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
