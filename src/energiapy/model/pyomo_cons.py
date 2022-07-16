#%%
"""pyomo constraints
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "0.0.1"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from pyomo.environ import ConcreteModel, Constraint
from ..utils.latex_utils import constraint_latex_render
from ..utils.model_utils import scale_list
from ..utils.model_utils import scale_pyomo_set
from ..utils.model_utils import scale_tuple
from ..components.location import Location


def nameplate_production_constraint(instance: ConcreteModel, location_set:set, network_scale_level:int = 0, scheduling_scale_level:int= 0) -> Constraint:
    """_summary_

    Args:
        instance (ConcreteModel): _description_
        location_set (set): _description_
        network_scale_level (int, optional): _description_. Defaults to 0.
        scheduling_scale_level (int, optional): _description_. Defaults to 0.

    Returns:
        Constraint: _description_
    """
    scale_levels = instance.scales.__len__()
    scales = scale_list(instance= instance, scale_levels = scale_levels)
    capacity_factor = {location.name: location.capacity_factor for location in location_set}    
    def nameplate_production_rule(instance, location, process, *scale_list):
        if process in instance.processes_varying:
            return instance.P[location, process, scale_list[:scheduling_scale_level+1]] <= \
                capacity_factor[location][process][scale_list[:scheduling_scale_level+1]]*instance.Cap_P[location, process, scale_list[:network_scale_level+1]]
        else:
            return instance.P[location, process, scale_list[:scheduling_scale_level+1]] <= instance.Cap_P[location, process, scale_list[:network_scale_level+1]]
    instance.nameplate_production_constraint = Constraint(
        instance.locations, instance.processes, *scales, rule=nameplate_production_rule, doc='nameplate production capacity constraint')
    constraint_latex_render(nameplate_production_rule)
    return instance.nameplate_production_constraint


def nameplate_inventory_constraint(instance: ConcreteModel, location_set:set, network_scale_level:int = 0, scheduling_scale_level:int= 0) -> Constraint: 
    scale_levels = instance.scales.__len__()
    scales = scale_list(instance= instance, scale_levels = scale_levels)
    loc_res_dict = {loc.name: {i.name for i in loc.resources} for loc in location_set}
    def nameplate_inventory_rule(instance, location, resource, *scale_list):
        if resource in instance.resources_store.intersection(loc_res_dict[location]):
            return instance.Inv[location, resource, scale_list[:scheduling_scale_level+1]] <= instance.Cap_S[location, resource, scale_list[:network_scale_level+1]]
        else:
            return instance.Inv[location, resource, scale_list[:scheduling_scale_level+1]] <= 0
    instance.nameplate_inventory_constraint = Constraint(
        instance.locations, instance.resources, *scales, rule=nameplate_inventory_rule, doc='nameplate inventory capacity constraint')
    constraint_latex_render(nameplate_inventory_rule)
    return instance.nameplate_inventory_constraint

def resource_consumption_constraint(instance: ConcreteModel, location_set:set, scheduling_scale_level:int= 0) -> Constraint:
    process_set = set().union(*[i.processes for i in location_set if i.processes is not None])
    resource_set = set().union(*[set(i.conversion.keys()) for i in list(process_set)])
    scale_levels = instance.scales.__len__()
    scales = scale_list(instance= instance, scale_levels = scale_levels)
    def resource_consumption_rule(instance, location, resource, *scale_list):
        return instance.C[location, resource, scale_list[:scheduling_scale_level+1]] <= next((resource_.consumption_max for resource_ in resource_set if resource_.name == resource))
    instance.resource_consumption_constraint = Constraint(
        instance.locations, instance.resources, *scales, rule=resource_consumption_rule, doc='resource consumption')
    constraint_latex_render(resource_consumption_rule)
    return instance.resource_consumption_constraint

def resource_expenditure_constraint(instance: ConcreteModel, location_set:set, scheduling_scale_level:int= 0, expenditure_scale_level:int= 0) -> Constraint:
    scale_levels = instance.scales.__len__()
    scales = scale_list(instance= instance, scale_levels = scale_levels)
    cost_factor = {location.name: location.cost_factor for location in location_set}
    cost = {location.name: location.resource_price for location in location_set}
    loc_res_dict = {loc.name: {i.name for i in loc.resources} for loc in location_set}
    def resource_expenditure_rule(instance, location, resource, *scale_list):
        if resource in instance.resources_varying.intersection(loc_res_dict[location]):
            return instance.B[location, resource, scale_list[:scheduling_scale_level+1]] == cost[location][resource]*\
                cost_factor[location][resource][scale_list[:expenditure_scale_level+1]]*instance.C[location, resource, scale_list[:scheduling_scale_level+1]]
        else:
            if resource in instance.resources_purch.intersection(loc_res_dict[location]):
                return instance.B[location, resource, scale_list[:scheduling_scale_level+1]] == cost[location][resource]*instance.C[location, resource, scale_list[:scheduling_scale_level+1]]      
            else:
                return instance.B[location, resource, scale_list[:scheduling_scale_level+1]] == 0     
    constraint_latex_render(resource_expenditure_rule)
    instance.resource_expenditure_constraint = Constraint(instance.locations, instance.resources, *scales, rule=resource_expenditure_rule, doc='expenditure on purchase of resource')
    return instance.resource_expenditure_constraint

def resource_discharge_constraint(instance: ConcreteModel, location_set:set, scheduling_scale_level:int= 0) -> Constraint:
    scale_levels = instance.scales.__len__()
    scales = scale_list(instance= instance, scale_levels = scale_levels)
    def resource_discharge_rule(instance, location, resource, *scale_list):
        if resource in instance.resource_nosell:
            return instance.S[location, resource, scale_list[:scheduling_scale_level+1]] == 0
    instance.resource_discharge_cons = Constraint(instance.locations, instance.resource_nosell, *scales, rule=resource_discharge_rule, doc='restrict discharge of non marketable resources')
    constraint_latex_render(resource_discharge_rule)
    return instance.resource_discharge_cons

def test_cycle(instance: ConcreteModel, location_set:set, scheduling_scale_level:int= 0) -> Constraint:
    scale_levels = instance.scales.__len__()
    scales = scale_list(instance= instance, scale_levels = scale_levels)
    scale_iter = scale_tuple(instance= instance, scale_levels = scale_levels)
    def test_cycle_rule(instance, location, resource, *scale_list):
        if scale_list[:scheduling_scale_level+1] != scale_iter[0]:
            return instance.Inv[location, resource, scale_list[:scheduling_scale_level+1]] - instance.Inv[location, resource, scale_iter[scale_iter.index(scale_list[:scheduling_scale_level+1]) -1]] == 0
        else:
            return instance.Inv[location, resource, scale_list[:scheduling_scale_level+1]] == 0
    instance.test_cycle_cons = Constraint(instance.locations, instance.resource_nosell, *scales, rule=test_cycle_rule, doc='restrict discharge of non marketable resources')
    constraint_latex_render(test_cycle)
    return instance.test_cycle_cons


# def inventory_balance_constraint(instance: ConcreteModel, location_set:set, scheduling_scale_level:int= 0) -> Constraint:
#     scale_levels = instance.scales.__len__()
#     scales = scale_list(instance= instance, scale_levels = scale_levels)
#     transport_list = [i for i in instance.transports]
#     def inventory_balance_rule(instance, location, resource, *scale_list):
#         #*GENERAL Inv t = Inv t-1 + P + C - S + Trans_in - Trans_out 
#         # Inv (location, resource, scale) = 
#         # Inv (location, resource, scale -1) 
#         # + sum over processes[Conv[process][resource]*P (location, process, scale)] 
#         # + C (location, resource, scale)
#         # - S(location, resource, scale)
#         # + Trans_in(location', location, resource, scale)
#         # - Trans_out(location, location', resource, scale) 
#         instance.Inv[location, resource, scale_list[:scheduling_scale_level+1]] ==  
        
        
        
#         if (hour == instance.hours.data()[0]) and (day == instance.days.data()[0]) and (instance.years.data()[0] == instance.horizon.data()[0]):
#             return instance.Inv[location, resource, hour, day, year] == \
#                 rep_days_dict[day]['cluster_wt']*(sum(conversion_dict[year][process][resource]*instance.P[location, process, hour, day, year] for process in instance.processes)
#                                                   + instance.C[location, resource, hour, day, year] - instance.S[location, resource, hour, day, year]) \
#                                                       + sum(sum(instance.Trans_in[location, location_ , resources, transport_, hours, days, year ] for location_ in location_list if location_ != location) for transport_ in transport_list) \
#                                                           - sum(sum(instance.Trans_in[location_, location , resources, transport_, hours, days, year ] for location_ in location_list if location_ != location) for transport_ in transport_list) \
                                                          
#         elif (hour == instance.hours.data()[0]) and (day == instance.days.data()[0]) and (instance.years.data()[0] > instance.horizon.data()[0]):
#             return instance.Inv[location, resource, hour, day, year] - (1 - next((resource_.loss for resource_ in resource_list if resource_.name == resource)))*results_dict[cost_scenario.name][instance.years.data()[0]- 1]['Sch_S'][location][resource][instance.days.data()[-1]][instance.hours.data()[-1]]['Inv']\
#                 == rep_days_dict[day]['cluster_wt']*(sum(conversion_dict[year][process][resource]*instance.P[location, process, hour, day, year] for process in instance.processes)
#                                                      + instance.C[location, resource, hour, day, year] - instance.S[location, resource, hour, day, year])\
#                                                          + sum(sum(instance.Trans_in[location, location_ , resources, transport_, hours, days, year ] for location_ in location_list if location_ != location) for transport_ in transport_list) \
#                                                           - sum(sum(instance.Trans_in[location_, location , resources, transport_, hours, days, year ] for location_ in location_list if location_ != location) for transport_ in transport_list) \
                                                          

#         elif (day > instance.days.data()[0]) and (hour == instance.hours.data()[0]):
#             return instance.Inv[location, resource, hour, day, year] - (1 - next((resource_.loss for resource_ in resource_list if resource_.name == resource)))*instance.Inv[location, resource, instance.hours.data()[-1], day-1, year]\
#                 == rep_days_dict[day]['cluster_wt']*(sum(conversion_dict[year][process][resource]*instance.P[location, process, hour, day, year] for process in instance.processes)
#                                                      + instance.C[location, resource, hour, day, year] - instance.S[location, resource, hour, day, year])\
#                                                          + sum(sum(instance.Trans_in[location, location_ , resources, transport_, hours, days, year ] for location_ in location_list if location_ != location) for transport_ in transport_list) \
#                                                           - sum(sum(instance.Trans_in[location_, location , resources, transport_, hours, days, year ] for location_ in location_list if location_ != location) for transport_ in transport_list) \
                                                          

#         else:
#             return instance.Inv[location, resource, hour, day, year] - (1 - next((resource_.loss for resource_ in resource_list if resource_.name == resource)))*instance.Inv[location, resource, hour-1, day, year] \
#                 == rep_days_dict[day]['cluster_wt']*(sum(conversion_dict[year][process][resource]*instance.P[location, process, hour, day, year] for process in instance.processes)
#                                                      + instance.C[location, resource, hour, day, year] - instance.S[location, resource, hour, day, year])\
#                                                          + sum(sum(instance.Trans_in[location, location_ , resources, transport_, hours, days, year ] for location_ in location_list if location_ != location) for transport_ in transport_list) \
#                                                           - sum(sum(instance.Trans_in[location_, location , resources, transport_, hours, days, year ] for location_ in location_list if location_ != location) for transport_ in transport_list) \
                                                          
#     instance.inventory_balance_constraint = Constraint(instance.locations, instance.resources, instance.hours, instance.days,
#                                                        instance.years, rule=inventory_balance_rule, doc='balances and cycles inventory between consecutive periods')
#     # if resource in ['Charge']:
#     #     print(instance.inventory_balance_constraint)
#     return instance.inventory_balance_constraint




#TODO - Demand constraint
#TODO - Production cost constraint
#TODO - carbon credit constraint


# *-------------------------Uncertainty Constraint------------------------------------


def uncertain_nameplate_production_constraint(instance: ConcreteModel, location_set:set, network_scale_level:int = 0, scheduling_scale_level:int= 0) -> Constraint:
    scale_levels = instance.scales.__len__()
    scales = scale_list(instance= instance, scale_levels = scale_levels)
    def uncertain_nameplate_production_rule(instance, location, process, *scale_list):
        if process in instance.processes_varying:
            return instance.P[location, process, scale_list[:scheduling_scale_level+1]] <= instance.Cap_P[location, process, scale_list[:network_scale_level+1]]\
                + instance.Delta_Cap_P[location, process, scale_list[:scheduling_scale_level+1]] 
        else:
            return instance.P[location, process, scale_list[:scheduling_scale_level+1]] <= instance.Cap_P[location, process, scale_list[:network_scale_level+1]]
    instance.uncertain_nameplate_production_constraint = Constraint(
        instance.locations, instance.processes, *scales, rule=uncertain_nameplate_production_rule, doc='nameplate production capacity constraint')
    constraint_latex_render(uncertain_nameplate_production_rule)
    return instance.uncertain_nameplate_production_constraint
   
def uncertain_resource_expenditure_constraint(instance: ConcreteModel, location_set:set, scheduling_scale_level:int= 0, expenditure_scale_level:int= 0) -> Constraint:
    scale_levels = instance.scales.__len__()
    scales = scale_list(instance= instance, scale_levels = scale_levels)
    cost = {location.name: location.resource_price for location in location_set}
    loc_res_dict = {loc.name: {i.name for i in loc.resources} for loc in location_set}
    def resource_expenditure_rule(instance, location, resource, *scale_list):
        if resource in instance.resources_varying.intersection(loc_res_dict[location]):
            return instance.B[location, resource, scale_list[:scheduling_scale_level+1]] == cost[location][resource]*\
                instance.C[location, resource, scale_list[:scheduling_scale_level+1]]*instance.Delta_Cost_R[location, resource, scale_list[:scheduling_scale_level+1]] 
        else:
            if resource in instance.resources_purch.intersection(loc_res_dict[location]):
                return instance.B[location, resource, scale_list[:scheduling_scale_level+1]] == cost[location][resource]*instance.C[location, resource, scale_list[:scheduling_scale_level+1]]      
            else:
                return instance.B[location, resource, scale_list[:scheduling_scale_level+1]] == 0     
    constraint_latex_render(resource_expenditure_rule)
    instance.resource_expenditure_constraint = Constraint(instance.locations, instance.resources, *scales, rule=resource_expenditure_rule, doc='expenditure on purchase of resource')
    return instance.resource_expenditure_constraint


# %%
