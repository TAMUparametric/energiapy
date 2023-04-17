
"""land variables
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "MIT"
__version__ = "1.0.5"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from pyomo.environ import ConcreteModel, Var, NonNegativeReals

from ...utils.scale_utils import scale_pyomo_set


def generate_land_vars(instance: ConcreteModel, scale_level: int = 0):
    """variables for land usage and costs

    Args:
        instance (ConcreteModel): pyomo instance
        scale_level (int, optional): scale at which credits are assigned. Defaults to 0.
    """
    instance.scales_land_network = scale_pyomo_set(
        instance=instance, scale_level=scale_level)
    instance.Land_process = Var(instance.locations, instance.processes,
                                instance.scales_land_network, within=NonNegativeReals, doc='Land cost by Process')
    instance.Land_location = Var(instance.locations, instance.scales_land_network,
                                 within=NonNegativeReals, doc='Land used at location')
    instance.Land_network = Var(
        instance.scales_land_network, within=NonNegativeReals, doc='Land used at network')

    instance.Land_cost_process = Var(instance.locations, instance.processes,
                                     instance.scales_land_network, within=NonNegativeReals, doc='Land used by Process')
    instance.Land_cost_location = Var(
        instance.locations, instance.scales_land_network, within=NonNegativeReals, doc='Land cost at location')
    instance.Land_cost_network = Var(
        instance.scales_land_network, within=NonNegativeReals, doc='Land cost at network')
    return