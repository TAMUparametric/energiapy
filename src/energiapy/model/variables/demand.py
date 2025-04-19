
"""demand variables
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2023, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "MIT"
__version__ = "1.0.7"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from pyomo.environ import ConcreteModel, Var, NonNegativeReals

from ...utils.scale_utils import scale_pyomo_set


def generate_demand_vars(instance: ConcreteModel, scale_level: int = 0):
    """variables for demand such as demand penalty

    Args:
        instance (ConcreteModel): pyomo instance
        scale_level (int, optional): scale at which credits are assigned. Defaults to 0.
    """

    instance.scales_demand = scale_pyomo_set(
        instance=instance, scale_level=scale_level)
    instance.Demand_penalty = Var(instance.locations, instance.resources_demand, instance.scales_demand,
                                  within=NonNegativeReals, doc='unmet demand at a location')
    instance.Demand_penalty_location = Var(instance.locations, instance.resources_demand, instance.scales_network,
                                           within=NonNegativeReals, doc='Total unmet demand at a location')
    instance.Demand_penalty_network = Var(instance.resources_demand, instance.scales_network,
                                          within=NonNegativeReals, doc='Total unmet demand from network')
    instance.Demand_penalty_cost = Var(instance.locations, instance.resources_demand, instance.scales_demand,
                                       within=NonNegativeReals, doc='penalty cost for unmet demand')
    instance.Demand_penalty_cost_location = Var(instance.locations, instance.resources_demand, instance.scales_network,
                                                within=NonNegativeReals, doc='Total penalty cost for unmet demand at a location')
    instance.Demand_penalty_cost_network = Var(instance.resources_demand, instance.scales_network,
                                               within=NonNegativeReals, doc='Total penalty cost for unmet demand from network')

    return

def generate_demand_backlog_vars(instance: ConcreteModel):
    instance.Demand_backlog = Var(instance.locations, instance.resources_demand, instance.scales_demand,
                                  within=NonNegativeReals, doc='backlog of demand at a location')
    instance.Demand_backlog_location = Var(instance.locations, instance.resources_demand, instance.scales_network,
                                           within=NonNegativeReals, doc='Total backlog demand at a location')
    instance.Demand_backlog_network = Var(instance.resources_demand, instance.scales_network,
                                          within=NonNegativeReals, doc='Total backlog from network')
    instance.Demand_backlog_cost = Var(instance.locations, instance.resources_demand, instance.scales_demand,
                                       within=NonNegativeReals, doc='backlog cost')
    instance.Demand_backlog_cost_location = Var(instance.locations, instance.resources_demand, instance.scales_network,
                                                within=NonNegativeReals, doc='Total backlog cost at a location')
    instance.Demand_backlog_cost_network = Var(instance.resources_demand, instance.scales_network,
                                               within=NonNegativeReals, doc='Total backlog cost from network')

def generate_demand_theta_vars(instance: ConcreteModel):
    """multiparametric variable for demand 

    Args:
        instance (ConcreteModel): pyomo instance
        scale_level (int, optional): scale at which credits are assigned. Defaults to 0.
    """

    instance.demand_theta = Var(instance.locations, instance.resources_demand, instance.scales_demand,
                                within=NonNegativeReals, doc='multiparametric variable for demand')

    return
