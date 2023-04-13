
"""Credit variables
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


def generate_credit_vars(instance: ConcreteModel, scale_level: int = 0):
    """variables for credits earned

    Args:
        instance (ConcreteModel): pyomo instance
        scale_level (int, optional): scale at which credits are assigned. Defaults to 0.
    """

    instance.scales_credit_network = scale_pyomo_set(
        instance=instance, scale_level=scale_level)
    instance.Credit_process = Var(instance.locations, instance.processes, instance.scales_credit_network,
                                  within=NonNegativeReals, doc='credit earned by each process')
    instance.Credit_location = Var(instance.locations,
                                   instance.scales_credit_network, within=NonNegativeReals, doc='credit earned at each location')
    instance.Credit_network = Var(instance.scales_credit_network,
                                  within=NonNegativeReals, doc='credit earned at network level')
    return
