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

from pyomo.environ import ConcreteModel, Constraint, Set #, OrderedSimpleSet, IndexedConstratint
from ..utils.latex_utils import constraint_latex_render
from ..utils.model_utils import scale_set, scale_list
from ..components.location import location



def nameplate_production_constraint(instance: ConcreteModel, location_set:set, network_scale_level:int = 0, scheduling_scale_level:int= 0):
    scale_level = max(network_scale_level, scheduling_scale_level)
    scales = scale_list(instance= instance, scale_level = scale_level)
    capacity_factor = {location.name: location.capacity_factor for location in location_set}
    
    #%%% use intersection of processes from location object and capacity factor processes 
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



def nameplate_inventory_constraint(instance: ConcreteModel, location_set:set, network_scale_level:int = 0, scheduling_scale_level:int= 0): 
    scale_level = max(network_scale_level, scheduling_scale_level)
    scales = scale_list(instance= instance, scale_level = scale_level)
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



def resource_consumption_constraint(instance: ConcreteModel, location_set:set, scheduling_scale_level:int= 0):
    process_set = set().union(*[i.processes for i in location_set if i.processes is not None])
    resource_set = set().union(*[set(i.conversion.keys()) for i in list(process_set)])
    scales = scale_list(instance= instance, scale_level = scheduling_scale_level)
    def resource_consumption_rule(instance, location, resource, *scale_list):
        return instance.C[location, resource, scale_list] <= next((resource_.consumption_max for resource_ in resource_set if resource_.name == resource))
    instance.resource_consumption_constraint = Constraint(
        instance.locations, instance.resources, *scales, rule=resource_consumption_rule, doc='resource consumption')
    constraint_latex_render(resource_consumption_rule)
    return instance.resource_consumption_constraint


def resource_expenditure_constraint(instance: ConcreteModel, location_set:set, scheduling_scale_level:int= 0, expenditure_scale_level:int= 0):
    scale_level = max(expenditure_scale_level, scheduling_scale_level)
    scales = scale_list(instance= instance, scale_level = scale_level)
    cost_factor = {location.name: location.cost_factor for location in location_set}
    cost = {location.name: location.resource_price for location in location_set}
    loc_res_dict = {loc.name: {i.name for i in loc.resources} for loc in location_set}
    def resource_expenditure_rule(instance, location, resource, *scale_list):
        if resource in instance.resources_varying.intersection(loc_res_dict[location]):
            return instance.B[location, resource, scale_list] == cost_factor[location][resource][scale_list[:expenditure_scale_level+1]]\
                *instance.C[location, resource, scale_list]
        else:
            if resource in instance.resources_purch.intersection(loc_res_dict[location]):
                return instance.B[location, resource, scale_list] == cost[location][resource]*instance.C[location, resource, scale_list]      
            else:
                return instance.B[location, resource, scale_list] == 0     
    constraint_latex_render(resource_expenditure_rule)
    instance.resource_expenditure_constraint = Constraint(instance.locations, instance.resources, *scales, rule=resource_expenditure_rule, doc='expenditure on purchase of resource')
    return instance.resource_expenditure_constraint



def resource_discharge_constraint(instance: ConcreteModel, scheduling_scale_level:int= 0):
    scales = scale_list(instance= instance, scale_level = scheduling_scale_level)
    def resource_discharge_rule(instance, location, resource, *scale_list):
        if resource in instance.resource_nosell:
            return instance.S[location, resource, scale_list] == 0
    instance.resource_discharge_cons = Constraint(instance.locations, instance.resource_nosell, *scales, rule=resource_discharge_rule, doc='restrict discharge of non marketable resources')
    constraint_latex_render(resource_discharge_rule)
    return instance.resource_discharge_cons

def uncertain_nameplate_production_constraint(instance: ConcreteModel, location_set:set, network_scale_level:int = 0, scheduling_scale_level:int= 0):
    scale_level = max(network_scale_level, scheduling_scale_level)
    scales = scale_list(instance= instance, scale_level = scale_level)
    
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
   

# %%
