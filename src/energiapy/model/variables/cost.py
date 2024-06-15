
"""pyomo variables
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


def generate_costing_vars(instance: ConcreteModel):
    # instance.cost_segments = Var(
    #     instance.locations, instance.processes, within=Binary, doc='Segment for costing')
    instance.Cost_network = Var(within=NonNegativeReals, doc='Total network cost')
    instance.Inv_cost = Var(instance.locations, instance.resources_store, instance.scales_network,
                            within=NonNegativeReals, doc='penalty incurred for storing resources')
    instance.Inv_cost_location = Var(instance.locations, instance.scales_network,
                                     within=NonNegativeReals, doc='penalty incurred for storing resources at location')
    instance.Inv_cost_network = Var(instance.scales_network,
                                    within=NonNegativeReals, doc='penalty incurred for storing resources at network')
    return
