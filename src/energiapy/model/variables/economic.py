from pyomo.environ import ConcreteModel, Var, NonNegativeReals, Set
from .variables import generate_var_loc_com_scn


def generate_total_cost_var(instance: ConcreteModel):
    instance.Cost_total = Var(
        within=NonNegativeReals, doc='Total expenditure across all locations summed over the network scale')


def generate_process_expenditure_vars(instance: ConcreteModel, scenario):
    if scenario.consider_capex:
        generate_var_loc_com_scn(instance=instance, var_name='Capex', tag='process',
                                 component_set='processes', label='Capital expenditure')
    if scenario.consider_fopex:
        generate_var_loc_com_scn(instance=instance, var_name='Fopex', tag='process',
                                 component_set='processes', label='Fixed operating expenditure')

    if scenario.consider_vopex:
        generate_var_loc_com_scn(instance=instance, var_name='Vopex', tag='process',
                                 component_set='processes', label='Variable operating expenditure')

    if scenario.consider_incidental:
        generate_var_loc_com_scn(instance=instance, var_name='Incidental', tag='process',
                                 component_set='processes', label='Incidental expenditure')


def generate_process_credit_vars(instance: ConcreteModel):
    generate_var_loc_com_scn(instance=instance, var_name='Credit', tag='process',
                             component_set='processes', label='Credits earned')


def generate_resource_expenditure_vars(instance: ConcreteModel, scenario):
    instance.B = Var(Set(initialize=[(i, j) for i in scenario.location_resource_purch_dict for j in scenario.location_resource_purch_dict[i]]),
                     instance.scales_scheduling, within=NonNegativeReals, doc='Purchase Expenditure')
    instance.B_location = Var(instance.locations, instance.resources_purch, instance.scales_network,
                              within=NonNegativeReals, doc='Total resource purchase at location')
    instance.B_network = Var(instance.resources_purch, instance.scales_network,
                             within=NonNegativeReals, doc='Total resource purchase from network')
    instance.B_total = Var(
        within=NonNegativeReals, doc='Total expenditure on resource purchase')

    if scenario.consider_storage_cost is True:
        generate_var_loc_com_scn(instance=instance, var_name='Inv_cost',
                                 tag='resource', component_set='resources_store', label='Inventory cost')


def generate_transport_expenditure_vars(instance: ConcreteModel):
    instance.Trans_cost_network = Var(instance.transports, instance.scales_network,
                                      within=NonNegativeReals, doc='cost of transportation for transport mode')

    instance.Capex_transport = Var(instance.sources, instance.sinks, instance.transports,
                                   instance.scales_network, within=NonNegativeReals, doc='capex to set up transport mode between sink and source')
    instance.Vopex_transport = Var(instance.sources, instance.sinks, instance.transports,
                                   instance.scales_network, within=NonNegativeReals, doc='vopex of transport mode between sink and source')
    instance.Fopex_transport = Var(instance.sources, instance.sinks, instance.transports,
                                   instance.scales_network, within=NonNegativeReals, doc='fopex of transport mode between sink and source')

    instance.Capex_transport_network = Var(
        instance.scales_network, within=NonNegativeReals, doc='overall capex for transport at the network level')
    instance.Vopex_transport_network = Var(
        instance.scales_network, within=NonNegativeReals, doc='overall vopex for transport at the network level')
    instance.Fopex_transport_network = Var(
        instance.scales_network, within=NonNegativeReals, doc='overall fopex for transport at the network level')

    instance.Capex_transport_total = Var(
        within=NonNegativeReals, doc='Total capital expenditure on transports')
    instance.Fopex_transport_total = Var(
        within=NonNegativeReals, doc='Total fixed expenditure on transports')
    instance.Vopex_transport_total = Var(
        within=NonNegativeReals, doc='Total variable expenditure on transports')


def generate_resource_revenue_vars(instance: ConcreteModel, scenario):

    instance.R = Var(Set(initialize=[(i, j) for i in scenario.location_resource_sell_dict for j in scenario.location_resource_sell_dict[i]]),
                     instance.scales_scheduling, within=NonNegativeReals, doc='Revenue from resource Sold')

    instance.R_location = Var(instance.locations, instance.resources_sell, instance.scales_network,
                              within=NonNegativeReals, doc='Total revenue from resource discharge at location')
    instance.R_network = Var(instance.resources_sell, instance.scales_network,
                             within=NonNegativeReals, doc='Total revenue from resource discharge from network')

    instance.R_total = Var(within=NonNegativeReals,
                           doc='Total revenue on resources sold')


# instance.cost_segments = Var(
#     instance.locations, instance.processes, within=Binary, doc='Segment for costing')
