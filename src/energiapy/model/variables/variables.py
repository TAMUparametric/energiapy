
"""
Key
loc: location
com: component
scn: network scale (temporal)
scs: scheduling scale (temporal)
"""

from pyomo.environ import ConcreteModel, NonNegativeReals, Var, Set


def generate_var_loc_com_scn(instance: ConcreteModel, var_name: str, tag: str, component_set: str, label: str):
    """generates network level decision variables of a the type: 
    (I) var(location, component, scales_network)
    (II) var(location, scales_network). Which is (I) summed over all components at location
    (III) var(scales_network). Which is (II) summed over all locations
    (IV) var(). Which is (III) summed over the network scale

    Args:
        instance (ConcreteModel): pyomo instance
        var_name (str): name for the decision variable
        tag (str): if an word is required to be tagged to (I). e.g.: Capex_process
        component_set (str): the set over which to write (II)
        label (str): what the variable means. e.g.: Capital expenditure for Capex 
    """
    locations = getattr(instance, 'locations')
    components = getattr(instance, component_set)
    scales_network = getattr(
        instance, 'scales_network')
    nn = NonNegativeReals
    setattr(instance, f'{var_name}_{tag}', Var(locations, components,
            scales_network, within=nn, doc=f'{label} for {tag}es'))
    setattr(instance, f'{var_name}_location', Var(
        locations, scales_network, within=nn, doc=f'{label} for all {tag}es at location'))
    setattr(instance, f'{var_name}_network', Var(
        scales_network, within=nn, doc=f'Total {label} for all locations'))
    setattr(instance, f'{var_name}_total', Var(within=nn,
            doc=f'Total {label} for all locations summed over network scale'))


def generate_var_loc_com_scn(instance: ConcreteModel, var_name: str, tag: str, component_set: str, label: str):
    """generates network level decision variables of a the type: 
    (I) var(location, component, scales_network)
    (II) var(location, scales_network). Which is (I) summed over all components at location
    (III) var(scales_network). Which is (II) summed over all locations
    (IV) var(). Which is (III) summed over the network scale

    Args:
        instance (ConcreteModel): pyomo instance
        var_name (str): name for the decision variable
        tag (str): if an word is required to be tagged to (I). e.g.: Capex_process
        component_set (str): the set over which to write (II)
        label (str): what the variable means. e.g.: Capital expenditure for Capex 
    """
    locations = getattr(instance, 'locations')
    components = getattr(instance, component_set)
    scales_network = getattr(
        instance, 'scales_network')
    nn = NonNegativeReals
    setattr(instance, f'{var_name}_{tag}', Var(locations, components,
            scales_network, within=nn, doc=f'{label} for {tag}es'))
    setattr(instance, f'{var_name}_location', Var(
        locations, scales_network, within=nn, doc=f'{label} for all {tag}es at location'))
    setattr(instance, f'{var_name}_network', Var(
        scales_network, within=nn, doc=f'Total {label} for all locations'))
    setattr(instance, f'{var_name}_total', Var(within=nn,
            doc=f'Total {label} for all locations summed over network scale'))

    # setattr(instance, f'{var_name}', Var(Set
    # instance.B = Var(Set(initialize=[(i, j) for i in scenario.location_resource_purch_dict for j in scenario.location_resource_purch_dict[i]]),
    #                  instance.scales_scheduling, within=NonNegativeReals, doc='Purchase Expenditure')
    # instance.B_location = Var(instance.locations, instance.resources_purch, instance.scales_network,
    #                           within=NonNegativeReals, doc='Total resource purchase at location')
    # instance.B_network = Var(instance.resources_purch, instance.scales_network,
    #                          within=NonNegativeReals, doc='Total resource purchase from network')
    # instance.B_total = Var(
    #     within=NonNegativeReals, doc='Total expenditure on resource purchase')

    # scenario.location_resource_purch_dict
    # scenario.location_resource_sell_dict
    # scenario.location_resource_sell_dict

    # scenario.location_process_dict

    # instance.R = Var(Set(initialize=[(i, j) for i in scenario.location_resource_sell_dict for j in scenario.location_resource_sell_dict[i]]),
    #                  instance.scales_scheduling, within=NonNegativeReals, doc='Revenue from resource Sold')

    # instance.R_location = Var(instance.locations, instance.resources_sell, instance.scales_network,
    #                           within=NonNegativeReals, doc='Total revenue from resource discharge at location')
    # instance.R_network = Var(instance.resources_sell, instance.scales_network,
    #                          within=NonNegativeReals, doc='Total revenue from resource discharge from network')

    # instance.R_total = Var(within=NonNegativeReals,
    #                        doc='Total revenue on resources sold')

    # instance.P = Var(Set(initialize=[(i, j) for i in scenario.location_process_dict for j in scenario.location_process_dict[i]]),
    #                  instance.scales_scheduling, within=NonNegativeReals, doc='Production')

    # instance.P_location = Var(instance.locations, instance.processes, instance.scales_network,
    #                           within=NonNegativeReals, doc='Total production at location')

    # instance.P_network = Var(instance.processes, instance.scales_network,
    #                          within=NonNegativeReals, doc='Total production from network')

    # instance.S = Var(Set(initialize=[(i, j) for i in scenario.location_resource_sell_dict for j in scenario.location_resource_sell_dict[i]]),
    #                  instance.scales_scheduling, within=NonNegativeReals, doc='Resource Dispensed/Sold')

    # instance.S_location = Var(instance.locations, instance.resources_sell, instance.scales_network,
    #                           within=NonNegativeReals, doc='Total resource discharge at location')

    # instance.S_network = Var(instance.resources_sell, instance.scales_network,
    #                          within=NonNegativeReals, doc='Total resource discharge from network')

    # instance.C = Var(Set(initialize=[(i, j) for i in scenario.location_resource_purch_dict for j in scenario.location_resource_purch_dict[i]]),
    #                  instance.scales_scheduling, within=NonNegativeReals, doc='Purchase Consumption')

    # instance.C_location = Var(instance.locations, instance.resources_purch, instance.scales_network,
    #                           within=NonNegativeReals, doc='Total resource consumption at location')

    # instance.C_network = Var(instance.resources_purch, instance.scales_network,
    #                          within=NonNegativeReals, doc='Total resource consumption from network')

    # instance.Inv = Var(instance.locations, instance.resources_store,
    #                    instance.scales_scheduling, within=NonNegativeReals, doc='Resource Inventory')

    # instance.Inv_location = Var(instance.locations, instance.resources_store,
    #                    instance.scales_scheduling, within=NonNegativeReals, doc='Resource Inventory')

    # instance.Inv_network = Var(instance.locations, instance.resources_store,
    #                            instance.scales_network, doc='Total inventory stored at location for resource')
