from enum import Enum, auto
from pyomo.environ import ConcreteModel, Constraint, Var, Set
from ...utils.scale_utils import scale_list, scale_tuple

class Cons(Enum):
    X_LEQ_B = auto()
    """
    x[:x_scale] <= b_factor[:b_scale].b
    """
    X_EQ_B = auto()
    """
    x[:x_scale] == b_factor[:b_scale].b
    """
    X_GEQ_B = auto()
    """
    x[:x_scale] >= b_factor[:b_scale].b
    """
    X_LEQ_BY = auto()
    """
    x[:x_scale] <= b_factor[:b_scale].b.y[:y_scale]
    """
    X_EQ_BY = auto()
    """
    x[:x_scale] == b_factor[:b_scale].b.y[:y_scale]
    """
    X_GEQ_BY = auto()
    """
    x[:x_scale] >= b_factor[:b_scale].b.y[:y_scale]
    """
    X_LEQ_Y = auto()
    """
    x[:x_scale] <= y[:y_scale]
    """
    X_EQ_Y = auto()
    """
    x[:x_scale] == y[:y_scale]
    """
    X_GEQ_Y = auto()
    """
    x[:x_scale] == y[:y_scale]
    """
    X_EQ_SUMSCALE_Y = auto()
    """
    x[:x_scale] == sum(y[:y_scale] for y_scale)
    """
    X_EQ_SUMLOC_Y = auto()
    """
    x[:x_scale] == sum(y[component,:y_scale] for all components in location)
    """
    X_EQ_SUMCOST_Y = auto()
    X_EQ_SUM_Y = auto()
    X_EQ_SUMCOMP_Y = auto()
    X_EQ_CY = auto()
    X_EQ_C = auto()
    X_EQ_SUMLOCCOST_Y = auto()


def printer(variable_x: str, variable_y: str, type_cons, print_once):
    if print_once:
        if type_cons == Cons.X_LEQ_B:
            print(f'{variable_x}<={variable_x}MAX')

        if type_cons == Cons.X_EQ_B:
            print(f'{variable_x}<=MAX')

        if type_cons == Cons.X_GEQ_B:
            print(f'{variable_x}>=MAX')

        if type_cons == Cons.X_LEQ_BY:
            print(f'{variable_x}<=(PARAM)*{variable_y}')

        if type_cons == Cons.X_EQ_BY:

            print(f'{variable_x}==(PARAM)*{variable_y}')

        if type_cons == Cons.X_GEQ_BY:

            print(f'{variable_x}>=(PARAM)*{variable_y}')

        if type_cons == Cons.X_LEQ_Y:
            print(f'{variable_x}<={variable_y}')

        if type_cons == Cons.X_EQ_Y:
            print(f'{variable_x}=={variable_y}')

        if type_cons == Cons.X_GEQ_Y:
            print(f'{variable_x}>={variable_y}')

        # if type_cons == Cons.X_EQ_SUMSCALE_Y:
        # if type_cons == Cons.X_EQ_SUMLOC_Y:
        # if type_cons == Cons.X_EQ_SUMCOST_Y:
        # if type_cons == Cons.X_EQ_SUM_Y:
        # if type_cons == Cons.X_EQ_SUMCOMP_Y:
        # if type_cons == Cons.X_EQ_CY:
        # if type_cons == Cons.X_EQ_C:


def make_constraint(instance: ConcreteModel, type_cons: Cons, variable_x: Var, location_set: Set, component_set: Set, b_max: dict = None,  loc_comp_dict: dict = None,
                    b_factor: dict = None, x_scale_level: int = 0, b_scale_level: int = 0, y_scale_level: int = 0, variable_y: Var = None, label: str = None,
                    c_component: dict = None, c_factor: dict = None, c_scale_level: int = 0, cluster_wt: dict = None) -> Constraint:
    """makes constraints of different types 

    Args:
        instance (ConcreteModel): pyomo instance
        type_cons (Cons): type of constraint from Cons enum class
        variable_x (Var): LHS variable 
        location_set (Set): pyomo set of locations
        component_set (Set): pyomo set of component (resource, material, process)
        b_max (dict, optional): RHS bound where b is of resolution (location, component, ..). Defaults to None.
        loc_comp_dict (dict, optional): dict with components in location. Defaults to None.
        b_factor (dict, optional): deterministic variability in RHS when using b. Defaults to None.
        x_scale_level (int, optional): scale of LHS variable. Defaults to 0.
        b_scale_level (int, optional): scale of determinstic variability in RHS when using b. Defaults to 0.
        y_scale_level (int, optional): scale of RHS variable. Defaults to 0.
        variable_y (Var, optional): RHS variable. Defaults to None.
        label (str, optional): description of constraint. Defaults to None.
        c_component (dict, optional): RHS bound where c is of resolution (component, ..) . Defaults to None.
        c_factor (dict, optional): deterministic variability in RHS when using c. Defaults to None.
        c_scale_level (int, optional): scale of deterministic variability in RHS when using c. Defaults to 0.
        cluster_wt (dict, optional): weight of AHC cluster. Defaults to None.

    Returns:
        Constraint: _description_
    """
    if b_scale_level is None:
        b_scale_level = 0

    if type_cons in [Cons.X_EQ_SUMLOC_Y, Cons.X_EQ_SUMSCALE_Y, Cons.X_EQ_SUM_Y, Cons.X_EQ_SUMCOMP_Y]:
        scales = scale_list(instance=instance,
                            scale_levels=x_scale_level + 1)
        scale_iter = scale_tuple(
            instance=instance, scale_levels=y_scale_level+1)
    else:
        scales = scale_list(instance=instance,
                            scale_levels=max(x_scale_level, y_scale_level, b_scale_level) + 1)

    # print_once = True
    # printer(variable_x, variable_y, type_cons, print_once)
    # print_once = False
    if type_cons == Cons.X_EQ_SUMLOC_Y:
        def cons_rule(instance, component, *scale):
            x = getattr(instance, variable_x)[
                component, scale[:x_scale_level + 1]]
            d_sum = sum(getattr(instance, variable_y)[location_, component, scale[
                :y_scale_level + 1]] for location_ in location_set)
            return x == d_sum

        return Constraint(component_set, *scales, rule=cons_rule, doc=label)

    elif type_cons == Cons.X_EQ_SUMLOCCOST_Y:
        def cons_rule(instance, location, *scale):
            x = getattr(instance, variable_x)[
                location, scale[:x_scale_level + 1]]
            d_sum = sum(getattr(instance, variable_y)[location, component_, scale[
                :y_scale_level + 1]] for component_ in component_set)
            return x == d_sum

        return Constraint(location_set, *scales, rule=cons_rule, doc=label)

    elif type_cons == Cons.X_EQ_SUMCOST_Y:
        def cons_rule(instance, *scale):
            x = getattr(instance, variable_x)[scale[:x_scale_level + 1]]
            d_sum = sum(getattr(instance, variable_y)[location_, scale[
                :y_scale_level + 1]] for location_ in location_set)
            return x == d_sum

        return Constraint(*scales, rule=cons_rule, doc=label)

    else:
        def cons_rule(instance, location, component, *scale):

            if type_cons == Cons.X_EQ_SUMCOMP_Y:

                x = getattr(instance, variable_x)[
                    location, scale[:x_scale_level + 1]]

            # elif type_cons == Cons.X_EQ_SUMCOST_Y:

            #     x = getattr(instance, variable_x)[
            #         scale[:x_scale_level + 1]]

            else:
                if component in loc_comp_dict[location]:
                    x = getattr(instance, variable_x)[
                        location, component, scale[:x_scale_level + 1]]
                else:
                    x = None

            def weight(x): return 1 if cluster_wt is None else cluster_wt[x]

            if (b_max is not None) and (component in loc_comp_dict[location]):
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
                if component in loc_comp_dict[location]:
                    if type_cons == Cons.X_EQ_SUMSCALE_Y:
                        d_sum = sum(weight(scale_)*getattr(instance, variable_y)[location, component, scale_[
                                    :y_scale_level + 1]] for scale_ in scale_iter if scale_[:x_scale_level + 1] == scale)
                    # elif type_cons == Cons.X_EQ_SUMLOC_Y:
                        # d_sum = sum(getattr(instance, variable_y)[location_, component, scale[
                        #             :y_scale_level + 1]] for location_ in location_set)
                    elif type_cons == Cons.X_EQ_SUM_Y:
                        d_sum = sum(getattr(instance, variable_y)[location_, scale[
                                    :y_scale_level + 1]] for location_ in location_set)
                    elif type_cons == Cons.X_EQ_SUMCOMP_Y:
                        d_sum = sum(getattr(instance, variable_y)[location, component_, scale[
                                    :y_scale_level + 1]] for component_ in component_set)
                    elif type_cons == Cons.X_EQ_SUMCOST_Y:
                        d_sum = sum(getattr(instance, variable_y)[location_, scale[
                                    :y_scale_level + 1]] for location_ in location_set)
                    else:
                        y = getattr(instance, variable_y)[
                            location, component, scale[:y_scale_level + 1]]
                else:
                    d_sum = None
                    y = None
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
                    if type_cons in [Cons.X_EQ_SUMSCALE_Y, Cons.X_EQ_SUMCOMP_Y, Cons.X_EQ_SUMCOST_Y]:
                        return x == d_sum
                else:
                    return Constraint.Skip

        return Constraint(location_set, component_set, *scales, rule=cons_rule, doc=label)


def constraint_sum_total(instance: ConcreteModel, var_total: str, var: str, network_scale_level: int = 0, label: str = None):
    """Find total cost across network and planning horizon

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        label (str, None): doc string for constraint
    """
    scale_iter = scale_tuple(
        instance=instance, scale_levels=network_scale_level + 1)

    if label is None:
        label = ''

    def constraint_sum_total_rule(instance):
        x_ = getattr(instance, var_total)
        y_sum = sum(getattr(instance, var)[scale_] for scale_ in scale_iter)
        return x_ == y_sum

    return Constraint(rule=constraint_sum_total_rule, doc=label)


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
