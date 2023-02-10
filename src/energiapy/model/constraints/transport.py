"""pyomo transport constraints
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "0.0.1"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from pyomo.environ import ConcreteModel, Constraint
from ...utils.latex_utils import constraint_latex_render
from ...utils.model_utils import scale_list
from ...utils.model_utils import scale_pyomo_set
from ...utils.model_utils import scale_tuple
from ...components.location import Location
from itertools import product
from typing import Union
from enum import Enum, auto




# *-------------------------Transport constraints--------------------------
def transport_export_constraint(instance: ConcreteModel, scheduling_scale_level: int = 0, transport_avail_dict: dict = {}) -> Constraint:
    scales = scale_list(instance=instance,
                        scale_levels=scheduling_scale_level+1)

    def transport_export_rule(instance, source, sink, resource, *scale_list):
        return instance.Exp[source, sink, resource, scale_list[:scheduling_scale_level+1]] == \
            sum(instance.Trans_exp[source, sink, resource, transport_, scale_list[:scheduling_scale_level+1]]
                for transport_ in instance.transports.intersection(transport_avail_dict[(source, sink)]))
    instance.transport_export_constraint = Constraint(instance.sources, instance.sinks,
                                                      instance.resources_trans, *scales, rule=transport_export_rule, doc='export of resource from source to sink')
    constraint_latex_render(transport_export_rule)
    return instance.transport_export_constraint


def transport_import_constraint(instance: ConcreteModel, scheduling_scale_level: int = 0, transport_avail_dict: dict = {}) -> Constraint:
    scales = scale_list(instance=instance,
                        scale_levels=scheduling_scale_level+1)

    def transport_import_rule(instance, sink, source, resource, *scale_list):
        return instance.Imp[sink, source, resource, scale_list[:scheduling_scale_level+1]] == \
            sum(instance.Trans_imp[sink, source, resource, transport_, scale_list[:scheduling_scale_level+1]]
                for transport_ in instance.transports.intersection(transport_avail_dict[(source, sink)]))
    instance.transport_import_constraint = Constraint(instance.sinks, instance.sources,
                                                      instance.resources_trans, *scales, rule=transport_import_rule, doc='import of resource from sink to source')
    constraint_latex_render(transport_import_rule)
    return instance.transport_import_constraint


def transport_balance_constraint(instance: ConcreteModel, scheduling_scale_level: int = 0) -> Constraint:
    scales = scale_list(instance=instance,
                        scale_levels=scheduling_scale_level+1)

    def transport_balance_rule(instance, sink, source, resource, *scale_list):
        return instance.Imp[sink, source, resource, scale_list[:scheduling_scale_level+1]] == instance.Exp[source, sink, resource, scale_list[:scheduling_scale_level+1]]
    instance.transport_balance_constraint = Constraint(instance.sinks, instance.sources,
                                                       instance.resources_trans, *scales, rule=transport_balance_rule, doc='balances import and export from source to sinks')
    constraint_latex_render(transport_balance_rule)
    return instance.transport_balance_constraint


def transport_exp_UB_constraint(instance: ConcreteModel, scheduling_scale_level: int = 0, trans_max: dict = {}, transport_avail_dict: dict = {}) -> Constraint:
    scales = scale_list(instance=instance,
                        scale_levels=scheduling_scale_level+1)

    def transport_exp_UB_rule(instance, source, sink, resource, transport, *scale_list):
        if transport in transport_avail_dict[(source, sink)]:
            return instance.Trans_exp[source, sink, resource, transport, scale_list[:scheduling_scale_level+1]] <= trans_max[transport]
        else:
            return instance.Trans_exp[source, sink, resource, transport, scale_list[:scheduling_scale_level+1]] <= 0
    instance.transport_exp_UB_constraint = Constraint(instance.sources, instance.sinks, instance.resources_trans,
                                                      instance.transports, *scales, rule=transport_exp_UB_rule, doc='import of resource from sink to source')
    constraint_latex_render(transport_exp_UB_rule)
    return instance.transport_exp_UB_constraint


def transport_imp_UB_constraint(instance: ConcreteModel, scheduling_scale_level: int = 0, trans_max: dict = {}, transport_avail_dict: dict = {}) -> Constraint:
    scales = scale_list(instance=instance,
                        scale_levels=scheduling_scale_level+1)

    def transport_imp_UB_rule(instance, sink, source, resource, transport, *scale_list):
        if transport in transport_avail_dict[(source, sink)]:
            return instance.Trans_imp[sink, source, resource, transport, scale_list[:scheduling_scale_level+1]] <= trans_max[transport]
        else:
            return instance.Trans_imp[sink, source, resource, transport, scale_list[:scheduling_scale_level+1]] <= 0
    instance.transport_imp_UB_constraint = Constraint(instance.sinks, instance.sources, instance.resources_trans,
                                                      instance.transports, *scales, rule=transport_imp_UB_rule, doc='import of resource from sink to source')
    constraint_latex_render(transport_imp_UB_rule)
    return instance.transport_imp_UB_constraint
