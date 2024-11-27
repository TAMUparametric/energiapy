"""emission variables
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2023, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "MIT"
__version__ = "1.0.5"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from pyomo.environ import ConcreteModel, NonNegativeReals, Var

from ...utils.scale_utils import scale_pyomo_set


def generate_emission_dynamic_vars(instance: ConcreteModel):
    """declares pyomo variables for emission at the chosen scale

    Args:
        instance (ConcreteModel): pyomo instance
        scale_level (int, optional):  scale for network variables. Defaults to 0.
    """
    # if not hasattr(instance, 'scales_emission_network'):
    #     instance.scales_emission_network = scale_pyomo_set(
    #         instance=instance, scale_level=scale_level)
    # if not hasattr(instance, 'carbon_emission_network'):
    #     instance.carbon_emission_network = Var(
    #         instance.scales_emission_network, within=NonNegativeReals, doc='Carbon emissions across network at network_scale')
    #     instance.carbon_emission_location = Var(instance.locations, instance.scales_emission_network,
    #                                             within=NonNegativeReals, doc='Carbon emissions at location at network_scale')

    # #Global warming potential section
    # if not hasattr(instance, 'global_warming_potential_location'):
    instance.global_warming_emissions_dynamic_total = Var(within=NonNegativeReals, doc = 'Total Global warming emissions for the horizon')