
"""uncertainty variables
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


def generate_uncertainty_vars(instance: ConcreteModel, scale_level: int = 0):
    """declares pyomo variables for uncertainty analysis of processes and resources

    Args:
        instance (ConcreteModel): pyomo instance
        scale_level (int, optional): scale for uncertainty. Defaults to 0.
    """
    instance.scales_uncertainty = scale_pyomo_set(
        instance, scale_level=scale_level)
   
    instance.resource_demand_uncertainty = Var(instance.locations, instance.resources_uncertain_demand,
                                               instance.scales_uncertainty, within=NonNegativeReals, doc='resource demand uncertainty')
    instance.resource_price_uncertainty = Var(instance.locations, instance.resources_uncertain_price,
                                              instance.scales_uncertainty, within=NonNegativeReals, doc='resource price uncertainty')
    instance.process_capacity_uncertainty = Var(instance.locations, instance.processes_uncertain_capacity,
                                                instance.scales_uncertainty, within=NonNegativeReals, doc='process capacity uncertainty')
    return
