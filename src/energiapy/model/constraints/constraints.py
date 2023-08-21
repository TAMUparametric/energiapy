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


def make_constraint(instance: ConcreteModel, type_cons: Cons, variable_x: Var, location_set: Set, component_set: Set, b_max: dict = None,  loc_comp_dict: dict = None,
                    b_factor: dict = None, a_scale_level: int = 0, b_scale_level: int = 0, variable_y: Var = None, label: str = None) -> Constraint:

    scales = scale_list(instance=instance,
                        scale_levels=len(instance.scales))

    def cons_rule(instance, location, component, *scale):
        x = getattr(instance, variable_x)[
            location, component, scale[:a_scale_level + 1]]

        if b_max is not None:
            bmax = b_max[location][component]
        else:
            bmax = 1

        if b_factor[location] is not None:
            bfactor = b_factor[location][component][scale[:b_scale_level + 1]
                                                    ]*b_max[location][component]
        else:
            bfactor = 1

        b = bmax*bfactor
        if variable_y is not None:
            y = getattr(instance, variable_y)[
                location, component, scale[:b_scale_level + 1]]

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
            else:
                return x == 0

    return Constraint(location_set, component_set, *scales, rule=cons_rule, doc=label)


class Constraints(Enum):
    """Class of b_traints
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
