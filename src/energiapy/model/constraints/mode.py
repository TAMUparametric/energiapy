"""pyomo production constraints
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
from ...utils.scale_utils import scale_list

def constraint_production_mode(instance: ConcreteModel, mode_dict:dict, scheduling_scale_level: int = 0) -> Constraint:
    """The sum of production through all modes equals production at scheduling scale

    Args:
        instance (ConcreteModel): pyomo model instance
        mode_dict (dict): dictionary with modes available for process
        scheduling_scale_level (int, optional): scale for scheduling decisions. Defaults to 0.

    Returns:
        Constraint: _description_
    """

    scales = scale_list(instance=instance, scale_levels=scheduling_scale_level+1)

    def production_mode_rule(instance, location, process, *scale_list):
        return instance.P[location, process, scale_list[:scheduling_scale_level+1]] == sum(instance.P_m[location, process, mode, scale_list[:scheduling_scale_level+1]] for mode in mode_dict[process])
    instance.constraint_production_mode = Constraint(instance.locations, instance.processes,
        *scales, rule=production_mode_rule, doc='production mode sum constraint')
    constraint_latex_render(production_mode_rule)
    return instance.constraint_production_mode



# def nameplate_production_rule(instance, location, process, *scale_list):
#         if process in loc_pro_dict[location]:
#             if process in instance.processes_varying:
#                 return instance.P[location, process, scale_list[:scheduling_scale_level+1]] <= \
#                     capacity_factor[location][process][scale_list[:scheduling_scale_level+1]] * \
#                     instance.Cap_P[location, process,
#                                 scale_list[:network_scale_level+1]]
#             else:
#                 return instance.P[location, process, scale_list[:scheduling_scale_level+1]] <= instance.Cap_P[location, process, scale_list[:network_scale_level+1]]
#         else:
#             return Constraint.Skip
