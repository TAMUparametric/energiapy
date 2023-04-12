
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
    instance.Cost = Var(within=NonNegativeReals, doc='Total cost')
    return
