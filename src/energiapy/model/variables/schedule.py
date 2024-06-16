from pyomo.environ import ConcreteModel, NonNegativeReals, Var, Set
from ...components.scenario import Scenario

def generate_scheduling_vars(instance: ConcreteModel, scenario: Scenario, mode_dict: dict = None):
    """declares pyomo variables for scheduling at the chosen scales


    Args:
        instance (ConcreteModel): pyomo instance
        scale_level (int, optional):  scale for scheduling variables. Defaults to 0.
        mode_dict (dict, optional): dictionary with mode information of processes. Defaults to None.
    """

    if mode_dict is None:
        mode_dict = dict()

    instance.P = Var(Set(initialize=[(i, j) for i in scenario.location_process_dict for j in scenario.location_process_dict[i]]),
                     instance.scales_scheduling, within=NonNegativeReals, doc='Production')

    instance.C = Var(Set(initialize=[(i, j) for i in scenario.location_resource_purch_dict for j in scenario.location_resource_purch_dict[i]]),
                     instance.scales_scheduling, within=NonNegativeReals, doc='Purchase Consumption')

    instance.S = Var(Set(initialize=[(i, j) for i in scenario.location_resource_sell_dict for j in scenario.location_resource_sell_dict[i]]),
                     instance.scales_scheduling, within=NonNegativeReals, doc='Resource Dispensed/Sold')

    instance.Inv = Var(instance.locations, instance.resources_store,
                       instance.scales_scheduling, within=NonNegativeReals, doc='Resource Inventory')

    # if len(instance.locations) > 1:
    #     instance.Imp = Var(instance.sinks, instance.sources, instance.resources_trans,
    #                        instance.scales_scheduling, within=NonNegativeReals, doc='Resource import')
    #     instance.Exp = Var(instance.sources, instance.sinks, instance.resources_trans,
    #                        instance.scales_scheduling, within=NonNegativeReals, doc='Resource export')
    # instance.P_m = Var(instance.locations, [(i, j) for i in mode_dict.keys(
    # ) for j in mode_dict[i]], instance.scales_scheduling, within=NonNegativeReals, doc='Production modes')
    
    
    
    instance.P_m = Var(Set(initialize=[(i, j, k) for i in scenario.location_process_dict for j in scenario.location_process_dict[i]
                       for k in mode_dict[j]]), instance.scales_scheduling, within=NonNegativeReals, doc='Production modes')
    # instance.P_m = Var(Set(initialize=[(instance.locations, [(i, j) for i in mode_dict.keys(
    # ) for j in mode_dict[i]])]), instance.scales_scheduling, within=NonNegativeReals, doc='Production modes')

    instance.P_material_m = Var(instance.locations, instance.processes, instance.material_modes,
                                instance.scales_scheduling, within=NonNegativeReals, doc='Production in material modes')


def generate_scheduling_theta_vars(instance: ConcreteModel):
    """declares multiparametric pyomo variables for scheduling at the chosen scales


    Args:
        instance (ConcreteModel): pyomo instance
    """

    instance.C_theta = Var(instance.locations, instance.resources_purch,
                           instance.scales_scheduling, within=NonNegativeReals, doc='Resource Consumption')
