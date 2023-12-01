"""transport constraints
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "MIT"
__version__ = "1.0.5"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from pyomo.environ import ConcreteModel, Constraint
from itertools import product

from ...utils.latex_utils import constraint_latex_render
from ...utils.scale_utils import scale_list, scale_tuple


def constraint_resource_export(instance: ConcreteModel, scheduling_scale_level: int = 0,
                               transport_avail_dict: dict = None, resource_transport_dict: dict = None,
                               source_sink_resource_dict: dict = None) -> Constraint:
    """Total resource exported equals amount transported through all modes

    Args:
        instance (ConcreteModel): pyomo model instance
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.
        transport_avail_dict (dict, optional): Modes of transportation available between locations. Defaults to {}.

    Returns:
        Constraint: resource_export
    """

    if transport_avail_dict is None:
        transport_avail_dict = dict()

    scales = scale_list(instance=instance,
                        scale_levels=scheduling_scale_level + 1)

    def resource_export_rule(instance, source, sink, resource, *scale_list):
        if resource in source_sink_resource_dict[(source, sink)]:
            return instance.Exp_R[source, sink, resource, scale_list[:scheduling_scale_level + 1]] == \
                sum(instance.Exp[source, sink, transport_, resource, scale_list[:scheduling_scale_level + 1]]
                    for transport_ in transport_avail_dict[(source, sink)] if transport_ in resource_transport_dict[resource])
        else:
            return instance.Exp_R[source, sink, resource, scale_list[:scheduling_scale_level + 1]] == 0
    instance.constraint_resource_export = Constraint(instance.sources, instance.sinks,
                                                     instance.resources_trans, *scales, rule=resource_export_rule,
                                                     doc='export of resource from source to sink')
    constraint_latex_render(resource_export_rule)
    return instance.constraint_resource_export


def constraint_transport_export(instance: ConcreteModel, scheduling_scale_level: int = 0,
                                transport_avail_dict: dict = None, transport_resource_dict: dict = None) -> Constraint:
    """Total resource exported equals amount transported through all modes

    Args:
        instance (ConcreteModel): pyomo model instance
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.
        transport_avail_dict (dict, optional): Modes of transportation available between locations. Defaults to {}.

    Returns:
        Constraint: transport_export
    """

    if transport_avail_dict is None:
        transport_avail_dict = dict()

    scales = scale_list(instance=instance,
                        scale_levels=scheduling_scale_level + 1)

    def transport_export_rule(instance, source, sink, transport, *scale_list):
        if transport in transport_avail_dict[(source, sink)]:
            return instance.Exp_F[source, sink, transport, scale_list[:scheduling_scale_level + 1]] == \
                sum(instance.Exp[source, sink, transport, resource_, scale_list[:scheduling_scale_level + 1]]
                    for resource_ in transport_resource_dict[transport])
        else:
            return instance.Exp_F[source, sink, transport, scale_list[:scheduling_scale_level + 1]] == 0
    instance.constraint_transport_export = Constraint(instance.sources, instance.sinks,
                                                      instance.transports, *scales, rule=transport_export_rule,
                                                      doc='export of resource from source to sink')
    constraint_latex_render(transport_export_rule)
    return instance.constraint_transport_export


def constraint_transport_export_network(instance: ConcreteModel, scheduling_scale_level: int = 0, network_scale_level: int = 0,
                                        transport_avail_dict: dict = None) -> Constraint:
    """_summary_

    Args:
        instance (ConcreteModel): _description_
        scheduling_scale_level (int, optional): _description_. Defaults to 0.
        network_scale_level (int, optional): _description_. Defaults to 0.
        transport_avail_dict (dict, optional): _description_. Defaults to None.

    Returns:
        Constraint: _description_
    """
    if transport_avail_dict is None:
        transport_avail_dict = dict()

    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    scale_iter = scale_tuple(
        instance=instance, scale_levels=scheduling_scale_level+1)

    def transport_export_network_rule(instance, source, sink, transport, *scale_list):
        if transport in transport_avail_dict[(source, sink)]:
            return instance.Exp_F_network[source, sink, transport, scale_list[:network_scale_level + 1]] == \
                sum(instance.Exp_F[source, sink, transport, scale_]
                    for scale_ in scale_iter if scale_[:network_scale_level + 1] == scale_list)
        else:
            return instance.Exp_F_network[source, sink, transport, scale_list[:scheduling_scale_level + 1]] == 0
    instance.constraint_transport_export_network = Constraint(instance.sources, instance.sinks,
                                                              instance.transports, *scales, rule=transport_export_network_rule,
                                                              doc='total export from transport mode from source to sink')
    constraint_latex_render(transport_export_network_rule)
    return instance.constraint_transport_export_network


def constraint_export(instance: ConcreteModel, scheduling_scale_level: int = 0, network_scale_level: int = 0,
                      location_transport_resource_dict: dict = None, transport_capacity_factor: dict = None, transport_capacity_scale_level: int = 0) -> Constraint:
    """Total resource exported equals amount transported through all modes

    Args:
        instance (ConcreteModel): pyomo model instance
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.
        transport_avail_dict (dict, optional): Modes of transportation available between locations. Defaults to {}.
        transport_capacity_factor (dict, None): capacity factor for transport mode. Defaults to None.
        transport_capacity_scale_level (int, None): scale level of variability for transport capacity factor

    Returns:
        Constraint: export
    """

    scales = scale_list(instance=instance,
                        scale_levels=scheduling_scale_level + 1)

    def export_rule(instance, source, sink, transport, *scale_list):
        if transport in location_transport_resource_dict[(source, sink)].keys():
            if transport in instance.transports_varying_capacity:
                return instance.Exp_F[source, sink, transport, scale_list[:scheduling_scale_level + 1]] <= transport_capacity_factor[(source, sink)][transport][scale_list[:transport_capacity_scale_level+1]]*instance.Cap_F[source, sink, transport, scale_list[:network_scale_level + 1]]
            else:
                return instance.Exp_F[source, sink, transport, scale_list[:scheduling_scale_level + 1]] <= instance.Cap_F[source, sink, transport, scale_list[:network_scale_level + 1]]
        else:
            return instance.Exp_F[source, sink, transport, scale_list[:scheduling_scale_level + 1]] == 0
    # in instance.resources_trans if resource_
    instance.constraint_export = Constraint(instance.sources, instance.sinks,
                                            instance.transports, *scales, rule=export_rule,
                                            doc='capacity bound export of resource from source to sink')
    constraint_latex_render(export_rule)
    return instance.constraint_export


def constraint_transport_capacity_LB(instance: ConcreteModel, network_scale_level: int = 0,
                                     trans_min: dict = None, transport_avail_dict: dict = None) -> Constraint:
    """Minimum capacity bound for transport mode

    Args:
        instance (ConcreteModel): pyomo model instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        trans_max (dict, optional): Maximum allowed transportation. Defaults to {}.
        transport_avail_dict (dict, optional): Modes of transportation available between locations. Defaults to {}.

    Returns:
        Constraint: transport_capacity_LB
    """

    if trans_min is None:
        trans_min = dict()

    if transport_avail_dict is None:
        transport_avail_dict = dict()

    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    def transport_capacity_LB_rule(instance, source, sink,  transport, *scale_list):
        if transport in transport_avail_dict[(source, sink)]:
            return instance.Cap_F[source, sink, transport, scale_list[:network_scale_level + 1]] >= \
                trans_min[transport] * instance.X_F[source, sink,
                                                    transport, scale_list[:network_scale_level + 1]]
        else:
            return instance.Cap_F[source, sink, transport, scale_list[:network_scale_level + 1]] == 0

    instance.constraint_transport_capacity_LB = Constraint(instance.sources, instance.sinks,
                                                           instance.transports, *scales, rule=transport_capacity_LB_rule,
                                                           doc='LB for transport capacity')
    constraint_latex_render(transport_capacity_LB_rule)
    return instance.constraint_transport_capacity_LB


def constraint_transport_capacity_UB(instance: ConcreteModel, network_scale_level: int = 0,
                                     trans_max: dict = None, transport_avail_dict: dict = None) -> Constraint:
    """Maximum capacity bound for transport mode

    Args:
        instance (ConcreteModel): pyomo model instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        trans_max (dict, optional): Maximum allowed transportation. Defaults to {}.
        transport_avail_dict (dict, optional): Modes of transportation available between locations. Defaults to {}.

    Returns:
        Constraint: transport_capacity_UB
    """

    if trans_max is None:
        trans_max = dict()

    if transport_avail_dict is None:
        transport_avail_dict = dict()

    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    def transport_capacity_UB_rule(instance, source, sink, transport, *scale_list):
        if transport in transport_avail_dict[(source, sink)]:
            return instance.Cap_F[source, sink, transport, scale_list[:network_scale_level + 1]] <= \
                trans_max[transport] * instance.X_F[source, sink,
                                                    transport, scale_list[:network_scale_level + 1]]
        else:
            return instance.Cap_F[source, sink, transport, scale_list[:network_scale_level + 1]] == 0

    instance.constraint_transport_capacity_UB = Constraint(instance.sources, instance.sinks,
                                                           instance.transports, *scales, rule=transport_capacity_UB_rule,
                                                           doc='UB for transport capacity')
    constraint_latex_render(transport_capacity_UB_rule)
    return instance.constraint_transport_capacity_UB



def constraint_transport_capacity_LB_no_bin(instance: ConcreteModel, network_scale_level: int = 0,
                                     trans_min: dict = None, transport_avail_dict: dict = None) -> Constraint:
    """Minimum capacity bound for transport mode

    Args:
        instance (ConcreteModel): pyomo model instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        trans_max (dict, optional): Maximum allowed transportation. Defaults to {}.
        transport_avail_dict (dict, optional): Modes of transportation available between locations. Defaults to {}.

    Returns:
        Constraint: transport_capacity_LB_no_bin
    """

    if trans_min is None:
        trans_min = dict()

    if transport_avail_dict is None:
        transport_avail_dict = dict()

    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    def transport_capacity_LB_no_bin_rule(instance, source, sink,  transport, *scale_list):
        if transport in transport_avail_dict[(source, sink)]:
            return instance.Cap_F[source, sink, transport, scale_list[:network_scale_level + 1]] >= \
                trans_min[transport] 
        else:
            return instance.Cap_F[source, sink, transport, scale_list[:network_scale_level + 1]] == 0

    instance.constraint_transport_capacity_LB_no_bin = Constraint(instance.sources, instance.sinks,
                                                           instance.transports, *scales, rule=transport_capacity_LB_no_bin_rule,
                                                           doc='LB_no_bin for transport capacity')
    constraint_latex_render(transport_capacity_LB_no_bin_rule)
    return instance.constraint_transport_capacity_LB_no_bin


def constraint_transport_capacity_UB_no_bin(instance: ConcreteModel, network_scale_level: int = 0,
                                     trans_max: dict = None, transport_avail_dict: dict = None) -> Constraint:
    """Maximum capacity bound for transport mode

    Args:
        instance (ConcreteModel): pyomo model instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        trans_max (dict, optional): Maximum allowed transportation. Defaults to {}.
        transport_avail_dict (dict, optional): Modes of transportation available between locations. Defaults to {}.

    Returns:
        Constraint: transport_capacity_UB_no_bin
    """

    if trans_max is None:
        trans_max = dict()

    if transport_avail_dict is None:
        transport_avail_dict = dict()

    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    def transport_capacity_UB_no_bin_rule(instance, source, sink, transport, *scale_list):
        if transport in transport_avail_dict[(source, sink)]:
            return instance.Cap_F[source, sink, transport, scale_list[:network_scale_level + 1]] <= \
                trans_max[transport] * instance.X_F[source, sink,
                                                    transport, scale_list[:network_scale_level + 1]]
        else:
            return instance.Cap_F[source, sink, transport, scale_list[:network_scale_level + 1]] == 0

    instance.constraint_transport_capacity_UB_no_bin = Constraint(instance.sources, instance.sinks,
                                                           instance.transports, *scales, rule=transport_capacity_UB_no_bin_rule,
                                                           doc='UB_no_bin for transport capacity')
    constraint_latex_render(transport_capacity_UB_no_bin_rule)
    return instance.constraint_transport_capacity_UB_no_bin


def constraint_transport_capex(instance: ConcreteModel, trans_capex: dict, distance_dict: dict, transport_avail_dict: dict, network_scale_level: int = 0):
    """_summary_

    Args:
        instance (ConcreteModel): _description_
        trans_capex (dict): _description_
        distance_dict (dict): _description_
        transport_avail_dict (dict): _description_
        network_scale_level (int, optional): _description_. Defaults to 0.

    Returns:
        _type_: _description_
    """
    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    def transport_capex_rule(instance, source, sink, transport, *scale_list):
        if transport in transport_avail_dict[(source, sink)]:
            return instance.Capex_transport[source, sink, transport, scale_list[:network_scale_level + 1]] == distance_dict[(source, sink)]*trans_capex[transport]*instance.Cap_F[source, sink, transport, scale_list[:network_scale_level + 1]]
        else:
            return instance.Capex_transport[source, sink, transport, scale_list[:network_scale_level + 1]] == 0
    instance.constraint_transport_capex = Constraint(
        instance.sources, instance.sinks, instance.transports, *scales, rule=transport_capex_rule, doc='transport capex calculation')

    constraint_latex_render(transport_capex_rule)
    return instance.constraint_transport_capex


def constraint_transport_fopex(instance: ConcreteModel, trans_fopex: dict, distance_dict: dict, transport_avail_dict: dict, network_scale_level: int = 0):
    """_summary_

    Args:
        instance (ConcreteModel): _description_
        trans_fopex (dict): _description_
        distance_dict (dict): _description_
        transport_avail_dict (dict): _description_
        network_scale_level (int, optional): _description_. Defaults to 0.

    Returns:
        _type_: _description_
    """
    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    def transport_fopex_rule(instance, source, sink, transport, *scale_list):
        if transport in transport_avail_dict[(source, sink)]:
            return instance.Fopex_transport[source, sink, transport, scale_list[:network_scale_level + 1]] == distance_dict[(source, sink)]*trans_fopex[transport]*instance.Cap_F[source, sink, transport, scale_list[:network_scale_level + 1]]
        else:
            return instance.Fopex_transport[source, sink, transport, scale_list[:network_scale_level + 1]] == 0
    instance.constraint_transport_fopex = Constraint(
        instance.sources, instance.sinks, instance.transports, *scales, rule=transport_fopex_rule, doc='transport fopex calculation')

    constraint_latex_render(transport_fopex_rule)
    return instance.constraint_transport_fopex


def constraint_transport_vopex(instance: ConcreteModel, trans_vopex: dict, distance_dict: dict, transport_avail_dict: dict, network_scale_level: int = 0):
    """_summary_

    Args:
        instance (ConcreteModel): _description_
        trans_vopex (dict): _description_
        distance_dict (dict): _description_
        transport_avail_dict (dict): _description_
        network_scale_level (int, optional): _description_. Defaults to 0.

    Returns:
        _type_: _description_
    """
    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    def transport_vopex_rule(instance, source, sink, transport, *scale_list):
        if transport in transport_avail_dict[(source, sink)]:
            return instance.Vopex_transport[source, sink, transport, scale_list[:network_scale_level + 1]] == distance_dict[(source, sink)]*trans_vopex[transport]*instance.Exp_F_network[source, sink, transport, scale_list[:network_scale_level + 1]]
        else:
            return instance.Vopex_transport[source, sink, transport, scale_list[:network_scale_level + 1]] == 0
    instance.constraint_transport_vopex = Constraint(
        instance.sources, instance.sinks, instance.transports, *scales, rule=transport_vopex_rule, doc='transport capex calculation')

    constraint_latex_render(transport_vopex_rule)
    return instance.constraint_transport_vopex


def constraint_transport_network_capex(instance: ConcreteModel, network_scale_level: int = 0):
    """_summary_

    Args:
        instance (ConcreteModel): _description_
        trans_capex (dict): _description_
        distance_dict (dict): _description_
        transport_avail_dict (dict): _description_
        network_scale_level (int, optional): _description_. Defaults to 0.

    Returns:
        _type_: _description_
    """
    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    def transport_network_capex_rule(instance, *scale_list):
        return instance.Capex_transport_network[scale_list[:network_scale_level + 1]] == sum(instance.Capex_transport[source_, sink_, transport_, scale_list[:network_scale_level+1]]
                                                                                             for source_, sink_, transport_ in product(instance.sources, instance.sinks, instance.transports))
    instance.constraint_transport_network_capex = Constraint(
        *scales, rule=transport_network_capex_rule, doc='transport capex calculation for network')

    constraint_latex_render(transport_network_capex_rule)
    return instance.constraint_transport_network_capex


def constraint_transport_network_fopex(instance: ConcreteModel, network_scale_level: int = 0):
    """_summary_

    Args:
        instance (ConcreteModel): _description_
        trans_fopex (dict): _description_
        distance_dict (dict): _description_
        transport_avail_dict (dict): _description_
        network_scale_level (int, optional): _description_. Defaults to 0.

    Returns:
        _type_: _description_
    """
    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    def transport_network_fopex_rule(instance, *scale_list):
        return instance.Fopex_transport_network[scale_list[:network_scale_level + 1]] == sum(instance.Fopex_transport[source_, sink_, transport_, scale_list[:network_scale_level+1]]
                                                                                             for source_, sink_, transport_ in product(instance.sources, instance.sinks, instance.transports))
    instance.constraint_transport_network_fopex = Constraint(
        *scales, rule=transport_network_fopex_rule, doc='transport fopex calculation for network')

    constraint_latex_render(transport_network_fopex_rule)
    return instance.constraint_transport_network_fopex


def constraint_transport_network_vopex(instance: ConcreteModel, network_scale_level: int = 0):
    """_summary_

    Args:
        instance (ConcreteModel): _description_
        trans_vopex (dict): _description_
        distance_dict (dict): _description_
        transport_avail_dict (dict): _description_
        network_scale_level (int, optional): _description_. Defaults to 0.

    Returns:
        _type_: _description_
    """
    scales = scale_list(instance=instance,
                        scale_levels=network_scale_level + 1)

    def transport_network_vopex_rule(instance, *scale_list):
        return instance.Vopex_transport_network[scale_list[:network_scale_level + 1]] == sum(instance.Vopex_transport[source_, sink_, transport_, scale_list[:network_scale_level+1]]
                                                                                             for source_, sink_, transport_ in product(instance.sources, instance.sinks, instance.transports))
    instance.constraint_transport_network_vopex = Constraint(
        *scales, rule=transport_network_vopex_rule, doc='transport vopex calculation for network')

    constraint_latex_render(transport_network_vopex_rule)
    return instance.constraint_transport_network_vopex


# def constraint_transport_import(instance: ConcreteModel, scheduling_scale_level: int = 0,
#                                 transport_avail_dict: dict = None) -> Constraint:
#     """Total amount of resource imported

#     Args:
#         instance (ConcreteModel): pyomo model instance
#         scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.
#         transport_avail_dict (dict, optional): Modes of transportation available between locations. Defaults to {}.

#     Returns:
#         Constraint: transport_import
#     """

#     if transport_avail_dict is None:
#         transport_avail_dict = dict()

#     scales = scale_list(instance=instance,
#                         scale_levels=scheduling_scale_level + 1)

#     def transport_import_rule(instance, sink, source, resource, *scale_list):
#         return instance.Imp[sink, source, resource, scale_list[:scheduling_scale_level + 1]] == \
#             sum(instance.Trans_imp[sink, source, resource, transport_, scale_list[:scheduling_scale_level + 1]]
#                 for transport_ in instance.transports.intersection(transport_avail_dict[(source, sink)]))

#     instance.constraint_transport_import = Constraint(instance.sinks, instance.sources,
#                                                       instance.resources_trans, *scales, rule=transport_import_rule,
#                                                       doc='import of resource from sink to source')
#     constraint_latex_render(transport_import_rule)
#     return instance.constraint_transport_import


# def constraint_transport_balance(instance: ConcreteModel, scheduling_scale_level: int = 0) -> Constraint:
#     """Imported resources from sink to source equals exported resources from sink to source

#     Args:
#         instance (ConcreteModel): pyomo model instance
#         scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.

#     Returns:
#         Constraint: transport_balance
#     """
#     scales = scale_list(instance=instance,
#                         scale_levels=scheduling_scale_level + 1)

#     def transport_balance_rule(instance, sink, source, resource, *scale_list):
#         return instance.Imp[sink, source, resource, scale_list[:scheduling_scale_level + 1]] == instance.Exp[
#             source, sink, resource, scale_list[:scheduling_scale_level + 1]]

#     instance.constraint_transport_balance = Constraint(instance.sinks, instance.sources,
#                                                        instance.resources_trans, *scales, rule=transport_balance_rule,
#                                                        doc='balances import and export from source to sinks')
#     constraint_latex_render(transport_balance_rule)
#     return instance.constraint_transport_balance


# def constraint_transport_imp_UB(instance: ConcreteModel, scheduling_scale_level: int = 0, network_scale_level: int = 0,
#                                 trans_max: dict = None, transport_avail_dict: dict = None) -> Constraint:
#     """Maximum amount of resource that can be imported

#     Args:
#         instance (ConcreteModel): pyomo model instance
#         scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.
#         trans_max (dict, optional): Maximum allowed transportation. Defaults to {}.
#         transport_avail_dict (dict, optional): Modes of transportation available between locations. Defaults to {}.

#     Returns:
#         Constraint: transport_imp_UB
#     """

#     if trans_max is None:
#         trans_max = dict()

#     if transport_avail_dict is None:
#         transport_avail_dict = dict()

#     scales = scale_list(instance=instance,
#                         scale_levels=scheduling_scale_level + 1)

#     def transport_imp_UB_rule(instance, sink, source, resource, transport, *scale_list):
#         if transport in transport_avail_dict[(source, sink)]:
#             return instance.Trans_imp[sink, source, resource, transport, scale_list[:scheduling_scale_level + 1]] <= \
#                 trans_max[transport] * instance.X_T[source, sink, transport, scale_list[:network_scale_level + 1]]
#         else:
#             return instance.Trans_imp[sink, source, resource, transport, scale_list[:scheduling_scale_level + 1]] <= 0

#     instance.constraint_transport_imp_UB = Constraint(instance.sinks, instance.sources, instance.resources_trans,
#                                                       instance.transports, *scales, rule=transport_imp_UB_rule,
#                                                       doc='import of resource from sink to source')
#     constraint_latex_render(transport_imp_UB_rule)
#     return instance.constraint_transport_imp_UB
