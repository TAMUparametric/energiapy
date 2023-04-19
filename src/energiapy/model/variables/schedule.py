# %%.
"""scheduling variables
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "MIT"
__version__ = "1.0.5"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from pyomo.environ import ConcreteModel, NonNegativeReals, Var

from ...utils.scale_utils import scale_pyomo_set


def generate_scheduling_vars(instance: ConcreteModel, scale_level: int = 0, mode_dict: dict = None):
    """declares pyomo variables for scheduling at the chosen scales


    Args:
        instance (ConcreteModel): pyomo instance
        scale_level (int, optional):  scale for scheduling variables. Defaults to 0.
        mode_dict (dict, optional): dictionary with mode information of processes. Defaults to None.
    """

    if mode_dict is None:
        mode_dict = dict()

    instance.scales_scheduling = scale_pyomo_set(
        instance=instance, scale_level=scale_level)
    instance.P = Var(instance.locations, instance.processes_full,
                     instance.scales_scheduling, within=NonNegativeReals, doc='Production')
    instance.B = Var(instance.locations, instance.resources_purch,
                     instance.scales_scheduling, within=NonNegativeReals, doc='Purchase Expenditure')
    instance.C = Var(instance.locations, instance.resources_purch,
                     instance.scales_scheduling, within=NonNegativeReals, doc='Resource Consumption')
    instance.S = Var(instance.locations, instance.resources_sell,
                     instance.scales_scheduling, within=NonNegativeReals, doc='Resource Dispensed/Sold')
    instance.Inv = Var(instance.locations, instance.resources_store,
                       instance.scales_scheduling, within=NonNegativeReals, doc='Resource Inventory')
    if len(instance.locations) > 1:
        instance.Imp = Var(instance.sinks, instance.sources, instance.resources_trans,
                           instance.scales_scheduling, within=NonNegativeReals, doc='Resource import')
        instance.Exp = Var(instance.sources, instance.sinks, instance.resources_trans,
                           instance.scales_scheduling, within=NonNegativeReals, doc='Resource export')
    instance.P_m = Var(instance.locations, [(i, j) for i in mode_dict.keys(
    ) for j in mode_dict[i]], instance.scales_scheduling, within=NonNegativeReals, doc='Production modes')
    return
