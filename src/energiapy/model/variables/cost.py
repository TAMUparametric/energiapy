from pyomo.environ import ConcreteModel, Var, NonNegativeReals, Set
from ...components.scenario import Scenario


def generate_costing_vars(instance: ConcreteModel, scenario: Scenario):
    # instance.cost_segments = Var(
    #     instance.locations, instance.processes, within=Binary, doc='Segment for costing')

    instance.B = Var(Set(initialize=[(i, j) for i in scenario.location_resource_purch_dict for j in scenario.location_resource_purch_dict[i]]),
                     instance.scales_scheduling, within=NonNegativeReals, doc='Purchase Expenditure')
    instance.R = Var(Set(initialize=[(i, j) for i in scenario.location_resource_sell_dict for j in scenario.location_resource_sell_dict[i]]),
                     instance.scales_scheduling, within=NonNegativeReals, doc='Revenue from resource Sold')

    instance.R_location = Var(instance.locations, instance.resources_sell, instance.scales_network,
                              within=NonNegativeReals, doc='Total revenue from resource discharge at location')
    instance.R_network = Var(instance.resources_sell, instance.scales_network,
                             within=NonNegativeReals, doc='Total revenue from resource discharge from network')
    instance.B_location = Var(instance.locations, instance.resources_purch, instance.scales_network,
                              within=NonNegativeReals, doc='Total resource purchase at location')
    instance.B_network = Var(instance.resources_purch, instance.scales_network,
                             within=NonNegativeReals, doc='Total resource purchase from network')

    instance.Fopex_process = Var(instance.locations, instance.processes,
                                 instance.scales_network, within=NonNegativeReals, doc='Fixed Opex for process')
    instance.Vopex_process = Var(instance.locations, instance.processes,
                                 instance.scales_network, within=NonNegativeReals, doc='Variable Opex for process')
    instance.Capex_process = Var(instance.locations, instance.processes,
                                 instance.scales_network, within=NonNegativeReals, doc='Capex for process')
    instance.Incidental_process = Var(instance.locations, instance.processes,
                                      instance.scales_network, within=NonNegativeReals, doc='Incidentals for process')

    instance.Fopex_location = Var(instance.locations, instance.scales_network,
                                  within=NonNegativeReals, doc='Fixed Opex at location scale')
    instance.Vopex_location = Var(instance.locations, instance.scales_network,
                                  within=NonNegativeReals, doc='Variable Opex at location scale')
    instance.Capex_location = Var(instance.locations, instance.scales_network,
                                  within=NonNegativeReals, doc='Capex at location scale')
    instance.Incidental_location = Var(
        instance.locations, instance.scales_network, within=NonNegativeReals, doc='Incidental at location scale')

    instance.Fopex_network = Var(
        instance.scales_network, within=NonNegativeReals, doc='Fixed Opex at network scale')
    instance.Vopex_network = Var(
        instance.scales_network, within=NonNegativeReals, doc='Variable Opex at network scale')
    instance.Capex_network = Var(
        instance.scales_network, within=NonNegativeReals, doc='Capex at network scale')
    instance.Incidental_network = Var(
        instance.scales_network, within=NonNegativeReals, doc='Incidental at network scale')

    if len(instance.locations) > 1:
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

    instance.Inv_cost = Var(instance.locations, instance.resources_store, instance.scales_network,
                            within=NonNegativeReals, doc='penalty incurred for storing resources')
    instance.Inv_cost_location = Var(instance.locations, instance.scales_network,
                                     within=NonNegativeReals, doc='penalty incurred for storing resources at location')
    instance.Inv_cost_network = Var(instance.scales_network,
                                    within=NonNegativeReals, doc='penalty incurred for storing resources at network')

    instance.Capex_total = Var(
        within=NonNegativeReals, doc='Total capital expenditure on processes')

    instance.Capex_transport_total = Var(
        within=NonNegativeReals, doc='Total capital expenditure on transports')

    instance.Vopex_total = Var(
        within=NonNegativeReals, doc='Total variable expenditure on processes')

    instance.Fopex_total = Var(
        within=NonNegativeReals, doc='Total fixed expenditure on processes')

    instance.B_total = Var(
        within=NonNegativeReals, doc='Total expenditure on resource purchase')

    instance.Vopex_transport_total = Var(
        within=NonNegativeReals, doc='Total variable expenditure on transports')

    instance.Fopex_transport_total = Var(
        within=NonNegativeReals, doc='Total fixed expenditure on transports')

    instance.Incidental_total = Var(
        within=NonNegativeReals, doc='Total incidental expenditure on processes')

    instance.Land_cost_total = Var(
        within=NonNegativeReals, doc='Total expenditure on land')

    instance.Credit_total = Var(
        within=NonNegativeReals, doc='Total expenditure on credit')

    instance.Inv_cost_total = Var(
        within=NonNegativeReals, doc='Total expenditure on resource storage')

    instance.Cost_total = Var(
        within=NonNegativeReals, doc='Total expenditure')
