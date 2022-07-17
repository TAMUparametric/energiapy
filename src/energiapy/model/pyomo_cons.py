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

#TODO - Demand constraint
#TODO - Production cost constraint
#TODO - carbon credit constraint

# *-------------------------Network decision constraints--------------------------------

def network_production_constraint(instance: ConcreteModel, prod_max:dict, loc_pro_dict:dict = {}, network_scale_level:int = 0) -> Constraint:
    scale_levels = instance.scales.__len__()
    scales = scale_list(instance= instance, scale_levels = scale_levels)
    def network_production_rule(instance, location, process, *scale_list):
        if process in loc_pro_dict[location]:
            return instance.Cap_P[location, process, scale_list[:network_scale_level+1]] <= prod_max[location][process]*\
                instance.X_P[location, process, scale_list[:network_scale_level+1]]     
        else:
            return instance.Cap_P[location, process, scale_list[:network_scale_level+1]] == 0
    instance.network_production_constraint = Constraint(instance.locations, instance.processes, *scales, rule= network_production_rule, doc = 'production facility sizing and location')
    constraint_latex_render(network_production_rule)
    return instance.network_production_constraint


def network_storage_constraint(instance: ConcreteModel, store_max:dict, loc_res_dict:dict = {},  network_scale_level:int = 0) -> Constraint:
    scale_levels = instance.scales.__len__()
    scales = scale_list(instance= instance, scale_levels = scale_levels)
    def network_storage_rule(instance, location, resource, *scale_list):
        if resource in loc_res_dict[location]:
            return instance.Cap_S[location, resource, scale_list[:network_scale_level+1]] <= store_max[location][resource]*\
                instance.X_S[location, resource, scale_list[:network_scale_level+1]]     
        else:
            return instance.Cap_S[location, resource, scale_list[:network_scale_level+1]] == 0
    instance.network_storage_constraint = Constraint(instance.locations, instance.resources_store, *scales, rule= network_storage_rule, doc = 'storage facility sizing and location')
    constraint_latex_render(network_storage_rule)
    return instance.network_storage_constraint

# *-------------------------Mass balance constraints------------------------------------

def nameplate_production_constraint(instance: ConcreteModel, capacity_factor:dict = {}, network_scale_level:int = 0, scheduling_scale_level:int= 0) -> Constraint:
    scale_levels = instance.scales.__len__()
    scales = scale_list(instance= instance, scale_levels = scale_levels)
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


def nameplate_inventory_constraint(instance: ConcreteModel, loc_res_dict:dict = {}, network_scale_level:int = 0, scheduling_scale_level:int= 0) -> Constraint: 
    scale_levels = instance.scales.__len__()
    scales = scale_list(instance= instance, scale_levels = scale_levels)
    def nameplate_inventory_rule(instance, location, resource, *scale_list):
        if resource in instance.resources_store.intersection(loc_res_dict[location]):
            return instance.Inv[location, resource, scale_list[:scheduling_scale_level+1]] <= instance.Cap_S[location, resource, scale_list[:network_scale_level+1]]
        else:
            return instance.Inv[location, resource, scale_list[:scheduling_scale_level+1]] <= 0
    instance.nameplate_inventory_constraint = Constraint(
        instance.locations, instance.resources, *scales, rule=nameplate_inventory_rule, doc='nameplate inventory capacity constraint')
    constraint_latex_render(nameplate_inventory_rule)
    return instance.nameplate_inventory_constraint

def resource_consumption_constraint(instance: ConcreteModel, loc_res_dict:dict = {}, cons_max:dict = {}, scheduling_scale_level:int= 0) -> Constraint:
    scale_levels = instance.scales.__len__()
    scales = scale_list(instance= instance, scale_levels = scale_levels)
    def resource_consumption_rule(instance, location, resource, *scale_list):
        if resource in loc_res_dict[location]:
            return instance.C[location, resource, scale_list[:scheduling_scale_level+1]] <= cons_max[location][resource]
        else:
            return instance.C[location, resource, scale_list[:scheduling_scale_level+1]] <= 0 
    instance.resource_consumption_constraint = Constraint(
        instance.locations, instance.resources, *scales, rule=resource_consumption_rule, doc='resource consumption')
    constraint_latex_render(resource_consumption_rule)
    return instance.resource_consumption_constraint

def resource_expenditure_constraint(instance: ConcreteModel, cost_factor:dict = {}, price:dict = {}, \
    loc_res_dict:dict = {}, scheduling_scale_level:int= 0, expenditure_scale_level:int= 0) -> Constraint:
    scale_levels = instance.scales.__len__()
    scales = scale_list(instance= instance, scale_levels = scale_levels)
    def resource_expenditure_rule(instance, location, resource, *scale_list):
        if resource in instance.resources_varying.intersection(loc_res_dict[location]):
            return instance.B[location, resource, scale_list[:scheduling_scale_level+1]] == price[location][resource]*\
                cost_factor[location][resource][scale_list[:expenditure_scale_level+1]]*instance.C[location, resource, scale_list[:scheduling_scale_level+1]]
        else:
            if resource in instance.resources_purch.intersection(loc_res_dict[location]):
                return instance.B[location, resource, scale_list[:scheduling_scale_level+1]] == price[location][resource]*instance.C[location, resource, scale_list[:scheduling_scale_level+1]]      
            else:
                return instance.B[location, resource, scale_list[:scheduling_scale_level+1]] == 0     
    constraint_latex_render(resource_expenditure_rule)
    instance.resource_expenditure_constraint = Constraint(instance.locations, instance.resources, *scales, rule=resource_expenditure_rule, doc='expenditure on purchase of resource')
    return instance.resource_expenditure_constraint

def resource_discharge_constraint(instance: ConcreteModel, scheduling_scale_level:int= 0) -> Constraint:
    scale_levels = instance.scales.__len__()
    scales = scale_list(instance= instance, scale_levels = scale_levels)
    def resource_discharge_rule(instance, location, resource, *scale_list):
        if resource in instance.resource_nosell:
            return instance.S[location, resource, scale_list[:scheduling_scale_level+1]] == 0
    instance.resource_discharge_constraint = Constraint(instance.locations, instance.resource_nosell, *scales, rule=resource_discharge_rule, doc='restrict discharge of non marketable resources')
    constraint_latex_render(resource_discharge_rule)
    return instance.resource_discharge_constraint

def test_cycle(instance: ConcreteModel,  scheduling_scale_level:int= 0) -> Constraint:
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

def inventory_balance_constraint(instance: ConcreteModel, scheduling_scale_level:int= 0, conversion:dict = {}) -> Constraint:
    scale_levels = instance.scales.__len__()
    scales = scale_list(instance= instance, scale_levels = scale_levels)
    scale_iter = scale_tuple(instance= instance, scale_levels = scale_levels)
    def inventory_balance_rule(instance, location, resource, *scale_list):
        if scale_list[:scheduling_scale_level+1] != scale_iter[0]:
            return instance.Inv[location, resource, scale_list[:scheduling_scale_level+1]] \
                - instance.Inv[location, resource, scale_iter[scale_iter.index(scale_list[:scheduling_scale_level+1]) -1]] \
                    + instance.S[location, resource, scale_list[:scheduling_scale_level+1]] \
                    - instance.C[location, resource, scale_list[:scheduling_scale_level+1]] \
                    - sum(conversion[process][resource]*instance.P[location, process, scale_list[:scheduling_scale_level+1]] for process in instance.processes) \
                        + sum(instance.Exp[source, location, resource, scale_list[:scheduling_scale_level+1]] for source in instance.sources if source != location if location in instance.sinks)\
                        - sum(instance.Imp[location, sink, resource, scale_list[:scheduling_scale_level+1]] for sink in instance.sinks if sink != location if location in instance.sources)\
                            == 0
        else:
            return instance.Inv[location, resource, scale_list[:scheduling_scale_level+1]] \
                    + instance.S[location, resource, scale_list[:scheduling_scale_level+1]] \
                    - instance.C[location, resource, scale_list[:scheduling_scale_level+1]] \
                    - sum(conversion[process][resource]*instance.P[location, process, scale_list[:scheduling_scale_level+1]] for process in instance.processes) \
                        + sum(instance.Exp[source, location, resource, scale_list[:scheduling_scale_level+1]] for source in instance.sources if source != location if location in instance.sinks)\
                        - sum(instance.Imp[location, sink, resource, scale_list[:scheduling_scale_level+1]] for sink in instance.sinks if sink != location if location in instance.sources)\
                        == 0
    instance.inventory_balance_constraint = Constraint(instance.locations, instance.resources, *scales, rule=inventory_balance_rule, doc='restrict discharge of non marketable resources')
    constraint_latex_render(inventory_balance_constraint)
    return instance.inventory_balance_constraint


# *-------------------------Total mass balance calculation constraints--------------------------


# *-------------------------Uncertainty analysis constraints------------------------------------

def uncertain_nameplate_production_constraint(instance: ConcreteModel, network_scale_level:int = 0, scheduling_scale_level:int= 0) -> Constraint:
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
   
def uncertain_resource_expenditure_constraint(instance: ConcreteModel, price:dict = {},  loc_res_dict:dict = {}, scheduling_scale_level:int= 0, expenditure_scale_level:int= 0) -> Constraint:
    scale_levels = instance.scales.__len__()
    scales = scale_list(instance= instance, scale_levels = scale_levels)
    def uncertain_resource_expenditure_rule(instance, location, resource, *scale_list):
        if resource in instance.resources_varying.intersection(loc_res_dict[location]):
            return instance.B[location, resource, scale_list[:scheduling_scale_level+1]] == price[location][resource]*\
                instance.C[location, resource, scale_list[:scheduling_scale_level+1]]*instance.Delta_Cost_R[location, resource, scale_list[:scheduling_scale_level+1]] 
        else:
            if resource in instance.resources_purch.intersection(loc_res_dict[location]):
                return instance.B[location, resource, scale_list[:scheduling_scale_level+1]] == price[location][resource]*instance.C[location, resource, scale_list[:scheduling_scale_level+1]]      
            else:
                return instance.B[location, resource, scale_list[:scheduling_scale_level+1]] == 0     
    constraint_latex_render(uncertain_resource_expenditure_rule)
    instance.uncertain_resource_expenditure_constraint = Constraint(instance.locations, instance.resources, *scales, rule=uncertain_resource_expenditure_rule, doc='expenditure on purchase of resource')
    return instance.uncertain_resource_expenditure_constraint


# %%
