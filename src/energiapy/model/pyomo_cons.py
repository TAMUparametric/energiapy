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
from itertools import product
from typing import Union

#TODO - carbon credit constraint

# *-------------------------Summing 
# constraints--------------------------------


# *-------------------------Network decision constraints--------------------------------

def production_facility_constraint(instance: ConcreteModel, prod_max:dict, loc_pro_dict:dict = {}, network_scale_level:int = 0) -> Constraint:
    """Determines where production facility of certain capacity is inserted at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        prod_max (dict): maximum production of process at location
        loc_pro_dict (dict, optional): production facilities avaiable at location. Defaults to {}.
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: production_facility_constraint
    """
    scales = scale_list(instance= instance, scale_levels = network_scale_level+1)
    def production_facility_rule(instance, location, process, *scale_list):
        if process in loc_pro_dict[location]:
            return instance.Cap_P[location, process, scale_list[:network_scale_level+1]] <= prod_max[location][process]*\
                instance.X_P[location, process, scale_list[:network_scale_level+1]]     
        else:
            return instance.Cap_P[location, process, scale_list[:network_scale_level+1]] == 0
    instance.production_facility_constraint = Constraint(instance.locations, instance.processes, *scales, rule= production_facility_rule, doc = 'production facility sizing and location')
    constraint_latex_render(production_facility_rule)
    return instance.production_facility_constraint

def production_facility_fix_constraint(instance: ConcreteModel, prod_max: dict, production_binaries: dict,loc_pro_dict:dict = {}, network_scale_level:int = 0) -> Constraint:
    """Determines where production facility of certain capacity is inserted at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        prod_max (dict): maximum production of process at location
        loc_pro_dict (dict, optional): production facilities avaiable at location. Defaults to {}.
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: production_facility_fix_constraint
    """
    scales = scale_list(instance= instance, scale_levels = network_scale_level+1)
    def production_facility_fix_rule(instance, location, process, *scale_list):
        if process in loc_pro_dict[location]:
            return instance.Cap_P[location, process, scale_list[:network_scale_level+1]] <= prod_max[location][process]*\
                production_binaries[(location, process, *scale_list[:network_scale_level+1])]     
        else:
            return instance.Cap_P[location, process, scale_list[:network_scale_level+1]] == 0
    instance.production_facility_fix_constraint = Constraint(instance.locations, instance.processes, *scales, rule= production_facility_fix_rule, doc = 'production facility sizing and location')
    constraint_latex_render(production_facility_fix_rule)
    return instance.production_facility_fix_constraint


def min_production_facility_constraint(instance: ConcreteModel, prod_min:dict, loc_pro_dict:dict = {}, network_scale_level:int = 0) -> Constraint:
    """Determines where production facility of certain capacity is inserted at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        prod_max (dict): maximum production of process at location
        loc_pro_dict (dict, optional): production facilities avaiable at location. Defaults to {}.
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: min_production_facility_constraint
    """
    scales = scale_list(instance= instance, scale_levels = network_scale_level+1)
    def min_production_facility_rule(instance, location, process, *scale_list):
        if process in loc_pro_dict[location]:
            return instance.Cap_P[location, process, scale_list[:network_scale_level+1]] >= prod_min[location][process]*\
                instance.X_P[location, process, scale_list[:network_scale_level+1]]    
        else:
            return Constraint.Skip 
    instance.min_production_facility_constraint = Constraint(instance.locations, instance.processes, *scales, rule= min_production_facility_rule, doc = 'production facility sizing and location')
    constraint_latex_render(min_production_facility_rule)
    return instance.min_production_facility_constraint


def storage_facility_constraint(instance: ConcreteModel, store_max:dict, loc_res_dict:dict = {},  network_scale_level:int = 0) -> Constraint:
    """Determines where storage facility of certain capacity is inserted at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        store_max (dict): maximum storage capacity of resource at location
        loc_res_dict (dict, optional): storage facilities for resource available at location. Defaults to {}.
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.


    Returns:
        Constraint: storage_facility_constraint
    """
    scales = scale_list(instance= instance, scale_levels = network_scale_level + 1)
    def storage_facility_rule(instance, location, resource, *scale_list):
        if resource in loc_res_dict[location]:
            return instance.Cap_S[location, resource, scale_list[:network_scale_level+1]] <= store_max[location][resource]*\
                instance.X_S[location, resource, scale_list[:network_scale_level+1]]     
        else:
            return instance.Cap_S[location, resource, scale_list[:network_scale_level+1]] == 0
    instance.storage_facility_constraint = Constraint(instance.locations, instance.resources_store, *scales, rule= storage_facility_rule, doc = 'storage facility sizing and location')
    constraint_latex_render(storage_facility_rule)
    return instance.storage_facility_constraint

def storage_facility_fix_constraint(instance: ConcreteModel, store_max:dict, storage_binaries:dict, loc_res_dict:dict = {},  network_scale_level:int = 0) -> Constraint:
    """Determines where storage facility of certain capacity is inserted at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        store_max (dict): maximum storage capacity of resource at location
        loc_res_dict (dict, optional): storage facilities for resource available at location. Defaults to {}.
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.


    Returns:
        Constraint: storage_facility_fix_constraint
    """
    scales = scale_list(instance= instance, scale_levels = network_scale_level + 1)
    def storage_facility_fix_rule(instance, location, resource, *scale_list):
        if resource in loc_res_dict[location]:
            return instance.Cap_S[location, resource, scale_list[:network_scale_level+1]] <= store_max[location][resource]*\
                storage_binaries[(location, resource, *scale_list[:network_scale_level+1])]     
        else:
            return instance.Cap_S[location, resource, scale_list[:network_scale_level+1]] == 0
    instance.storage_facility_fix_constraint = Constraint(instance.locations, instance.resources_store, *scales, rule= storage_facility_fix_rule, doc = 'storage facility sizing and location')
    constraint_latex_render(storage_facility_fix_rule)
    return instance.storage_facility_fix_constraint


def min_storage_facility_constraint(instance: ConcreteModel, store_min:dict, loc_res_dict:dict = {},  network_scale_level:int = 0) -> Constraint:
    """Determines where storage facility of certain capacity is inserted at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        store_max (dict): maximum storage capacity of resource at location
        loc_res_dict (dict, optional): storage facilities for resource available at location. Defaults to {}.
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.


    Returns:
        Constraint: min_storage_facility_constraint
    """
    scales = scale_list(instance= instance, scale_levels = network_scale_level + 1)
    def min_storage_facility_rule(instance, location, resource, *scale_list):
        if resource in loc_res_dict[location]:
            return instance.Cap_S[location, resource, scale_list[:network_scale_level+1]] >= store_min[location][resource]*\
                instance.X_S[location, resource, scale_list[:network_scale_level+1]]   
        else:
            return Constraint.Skip   
    instance.min_storage_facility_constraint = Constraint(instance.locations, instance.resources_store, *scales, rule= min_storage_facility_rule, doc = 'storage facility sizing and location')
    constraint_latex_render(min_storage_facility_rule)
    return instance.min_storage_facility_constraint



# *-------------------------Mass balance constraints------------------------------------

def nameplate_production_constraint(instance: ConcreteModel, capacity_factor:dict = {}, network_scale_level:int = 0, scheduling_scale_level:int= 0) -> Constraint:
    """Determines production capacity utilization of facilities at location in network and capacity of facilities 

    Args:
        instance (ConcreteModel): pyomo instance
        capacity_factor (dict, optional): uncertain capacity availability training data. Defaults to {}.
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.

    Returns:
        Constraint: nameplate_production_constraint
    """
    scales = scale_list(instance= instance, scale_levels = instance.scales.__len__())
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
    """Determines storage capacity utilization for resource at location in network and capacity of facilities 

    Args:
        instance (ConcreteModel): pyomo instance
        loc_res_dict (dict, optional): storage facilities for resource available at location. Defaults to {}.
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.

    Returns:
        Constraint: nameplate_inventory_constraint
    """
    scales = scale_list(instance= instance, scale_levels = instance.scales.__len__())
    def nameplate_inventory_rule(instance, location, resource, *scale_list):
        if resource in loc_res_dict[location]:
            return instance.Inv[location, resource, scale_list[:scheduling_scale_level+1]] <= instance.Cap_S[location, resource, scale_list[:network_scale_level+1]]
        else:
            return instance.Inv[location, resource, scale_list[:scheduling_scale_level+1]] <= 0
    instance.nameplate_inventory_constraint = Constraint(
        instance.locations, instance.resources_store, *scales, rule=nameplate_inventory_rule, doc='nameplate inventory capacity constraint')
    constraint_latex_render(nameplate_inventory_rule)
    return instance.nameplate_inventory_constraint



def resource_consumption_constraint(instance: ConcreteModel, loc_res_dict:dict = {}, cons_max:dict = {}, scheduling_scale_level:int= 0) -> Constraint:
    """Determines consumption of resource at location in network 

    Args:
        instance (ConcreteModel): pyomo instance
        loc_res_dict (dict, optional): storage facilities for resource available at location. Defaults to {}.
        cons_max (dict, optional): maximum allowed consumption of resource at location. Defaults to {}.
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.

    Returns:
        Constraint: resource_consumption_constraint
    """
    scales = scale_list(instance= instance, scale_levels = instance.scales.__len__())
    def resource_consumption_rule(instance, location, resource, *scale_list):
        if resource in loc_res_dict[location]:
            return instance.C[location, resource, scale_list[:scheduling_scale_level+1]] <= cons_max[location][resource]
        else:
            return instance.C[location, resource, scale_list[:scheduling_scale_level+1]] <= 0 
    instance.resource_consumption_constraint = Constraint(
        instance.locations, instance.resources_purch, *scales, rule=resource_consumption_rule, doc='resource consumption')
    constraint_latex_render(resource_consumption_rule)
    return instance.resource_consumption_constraint

def resource_purchase_constraint(instance: ConcreteModel, cost_factor:dict = {}, price:dict = {}, \
    loc_res_dict:dict = {}, scheduling_scale_level:int= 0, expenditure_scale_level:int= 0) -> Constraint:
    """Determines expenditure on resource at location in network at the scheduling/expenditure scale

    Args:
        instance (ConcreteModel): pyomo instance
        cost_factor (dict, optional): uncertain cost training data. Defaults to {}.
        price (dict, optional): base price of resource. Defaults to {}.
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.
        expenditure_scale_level (int, optional): scale of resource purchase decisions. Defaults to 0.

    Returns:
        Constraint: resource_purchase_constraint
    """
    scales = scale_list(instance= instance, scale_levels = instance.scales.__len__())
    def resource_purchase_rule(instance, location, resource, *scale_list):
        if resource in instance.resources_varying.intersection(loc_res_dict[location]):
            return instance.B[location, resource, scale_list[:scheduling_scale_level+1]] == price[location][resource]*\
                cost_factor[location][resource][scale_list[:expenditure_scale_level+1]]*instance.C[location, resource, scale_list[:scheduling_scale_level+1]]
        else:
            if resource in instance.resources_purch.intersection(loc_res_dict[location]):
                return instance.B[location, resource, scale_list[:scheduling_scale_level+1]] == price[location][resource]*instance.C[location, resource, scale_list[:scheduling_scale_level+1]]      
            else:
                return instance.B[location, resource, scale_list[:scheduling_scale_level+1]] == 0     
    constraint_latex_render(resource_purchase_rule)
    instance.resource_purchase_constraint = Constraint(instance.locations, instance.resources_purch, *scales, rule=resource_purchase_rule, doc='expenditure on purchase of resource')
    return instance.resource_purchase_constraint

# def test_cycle(instance: ConcreteModel,  scheduling_scale_level:int= 0) -> Constraint:
#     """TEST CONSTRAINT
#     """
#     scales = scale_list(instance= instance, scale_levels = instance.scales.__len__())
#     scale_iter = scale_tuple(instance= instance, scale_levels = instance.scales.__len__())
#     def test_cycle_rule(instance, location, resource, *scale_list):
#         if scale_list[:scheduling_scale_level+1] != scale_iter[0]:
#             return instance.Inv[location, resource, scale_list[:scheduling_scale_level+1]] - instance.Inv[location, resource, scale_iter[scale_iter.index(scale_list[:scheduling_scale_level+1]) -1]] == 0
#         else:
#             return instance.Inv[location, resource, scale_list[:scheduling_scale_level+1]] == 0
#     instance.test_cycle_cons = Constraint(instance.locations, instance.resource_nosell, *scales, rule=test_cycle_rule, doc='test cycle')
#     constraint_latex_render(test_cycle)
#     return instance.test_cycle_cons

def inventory_balance_constraint(instance: ConcreteModel, scheduling_scale_level:int= 0, conversion:dict = {}) -> Constraint:
    """balances resource across the scheduling horizon

    Args:
        instance (ConcreteModel): pyomo instance
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.
        conversion (dict, optional): unit conversion of resource by production facility. Defaults to {}.

    Returns:
        Constraint: inventory_balance_constraint
    """
    scales = scale_list(instance= instance, scale_levels = instance.scales.__len__())
    scale_iter = scale_tuple(instance= instance, scale_levels = instance.scales.__len__())
    def inventory_balance_rule(instance, location, resource, *scale_list):
        if resource in instance.resources_purch:
            consumption = instance.C[location, resource, scale_list[:scheduling_scale_level+1]]
        else:
            consumption = 0
        
        if resource in instance.resources_store:
            if scale_list[:scheduling_scale_level+1] != scale_iter[0]:
                storage = instance.Inv[location, resource, scale_list[:scheduling_scale_level+1]] \
                        - instance.Inv[location, resource, scale_iter[scale_iter.index(scale_list[:scheduling_scale_level+1]) -1]] 
            else:
                storage = instance.Inv[location, resource, scale_list[:scheduling_scale_level+1]] 
        else:
            storage = 0

        if resource in instance.resources_sell:
            discharge = instance.S[location, resource, scale_list[:scheduling_scale_level+1]]
        else:
            discharge = 0
        
        if len(instance.locations) > 1:
            if resource in instance.resources_trans:
                transport =  sum(instance.Imp[location, source_, resource, scale_list[:scheduling_scale_level+1]] for source_ in instance.sources if source_ != location if location in instance.sinks)\
                                - sum(instance.Exp[location, sink_, resource, scale_list[:scheduling_scale_level+1]] for sink_ in instance.sinks if sink_ != location if location in instance.sources)\

            else:
                transport = 0
        else:
            transport = 0

        produced = sum(conversion[process][resource]*instance.P[location, process, scale_list[:scheduling_scale_level+1]] for process in instance.processes)
        
        return  consumption + produced - storage - discharge + transport  == 0

    instance.inventory_balance_constraint = Constraint(instance.locations, instance.resources, *scales, rule=inventory_balance_rule, doc='mass balance across scheduling scale')
    constraint_latex_render(inventory_balance_constraint)
    return instance.inventory_balance_constraint


# *-------------------------Transport constraints--------------------------
def transport_export_constraint(instance:ConcreteModel, scheduling_scale_level:int= 0, transport_avail_dict:dict = {}) -> Constraint:
    scales = scale_list(instance= instance, scale_levels= scheduling_scale_level+1)
    def transport_export_rule(instance, source, sink, resource, *scale_list):
        return instance.Exp[source, sink, resource, scale_list[:scheduling_scale_level+1]] == \
            sum(instance.Trans_exp[source, sink, resource, transport_, scale_list[:scheduling_scale_level+1]] \
                for transport_ in instance.transports.intersection(transport_avail_dict[(source, sink)]))
    instance.transport_export_constraint = Constraint(instance.sources, instance.sinks, \
        instance.resources_trans, *scales, rule=transport_export_rule, doc='export of resource from source to sink')
    constraint_latex_render(transport_export_rule)
    return instance.transport_export_constraint


def transport_import_constraint(instance:ConcreteModel, scheduling_scale_level:int= 0, transport_avail_dict:dict = {}) -> Constraint:
    scales = scale_list(instance= instance, scale_levels= scheduling_scale_level+1)
    def transport_import_rule(instance, sink, source, resource, *scale_list):
        return instance.Imp[sink, source, resource, scale_list[:scheduling_scale_level+1]] == \
            sum(instance.Trans_imp[sink, source, resource, transport_, scale_list[:scheduling_scale_level+1]] \
                for transport_ in instance.transports.intersection(transport_avail_dict[(source, sink)]))
    instance.transport_import_constraint = Constraint(instance.sinks, instance.sources, \
        instance.resources_trans, *scales, rule=transport_import_rule, doc='import of resource from sink to source')
    constraint_latex_render(transport_import_rule)
    return instance.transport_import_constraint

def transport_balance_constraint(instance:ConcreteModel, scheduling_scale_level:int= 0) -> Constraint:
    scales = scale_list(instance= instance, scale_levels= scheduling_scale_level+1)
    def transport_balance_rule(instance, sink, source, resource, *scale_list):
        return instance.Imp[sink, source, resource, scale_list[:scheduling_scale_level+1]] == instance.Exp[source, sink, resource, scale_list[:scheduling_scale_level+1]]
    instance.transport_balance_constraint = Constraint(instance.sinks, instance.sources, \
        instance.resources_trans, *scales, rule=transport_balance_rule, doc='balances import and export from source to sinks')
    constraint_latex_render(transport_balance_rule)
    return instance.transport_balance_constraint

def transport_exp_UB_constraint(instance:ConcreteModel, scheduling_scale_level: int= 0, trans_max:dict = {}, transport_avail_dict:dict = {}) -> Constraint:
    scales = scale_list(instance= instance, scale_levels= scheduling_scale_level+1)
    def transport_exp_UB_rule(instance, source, sink, resource, transport, *scale_list):
        if transport in transport_avail_dict[(source, sink)]:
            return instance.Trans_exp[source, sink, resource, transport, scale_list[:scheduling_scale_level+1]] <= trans_max[transport]
        else:
            return instance.Trans_exp[source, sink, resource, transport, scale_list[:scheduling_scale_level+1]] <= 0
    instance.transport_exp_UB_constraint = Constraint(instance.sources, instance.sinks, instance.resources_trans, instance.transports, *scales, rule=transport_exp_UB_rule, doc='import of resource from sink to source')
    constraint_latex_render(transport_exp_UB_rule)
    return instance.transport_exp_UB_constraint

def transport_imp_UB_constraint(instance:ConcreteModel, scheduling_scale_level: int= 0, trans_max:dict = {}, transport_avail_dict:dict = {}) -> Constraint:
    scales = scale_list(instance= instance, scale_levels= scheduling_scale_level+1)
    def transport_imp_UB_rule(instance, sink, source, resource, transport, *scale_list):
        if transport in transport_avail_dict[(source, sink)]:
            return instance.Trans_imp[sink, source, resource, transport, scale_list[:scheduling_scale_level+1]] <= trans_max[transport]
        else:
            return instance.Trans_imp[sink, source, resource, transport, scale_list[:scheduling_scale_level+1]] <= 0
    instance.transport_imp_UB_constraint = Constraint(instance.sinks, instance.sources, instance.resources_trans, instance.transports, *scales, rule=transport_imp_UB_rule, doc='import of resource from sink to source')
    constraint_latex_render(transport_imp_UB_rule)
    return instance.transport_imp_UB_constraint

def transport_exp_cost_constraint(instance:ConcreteModel, scheduling_scale_level: int= 0, trans_cost:dict = {}, distance_dict:dict = {}) -> Constraint:
    scales = scale_list(instance= instance, scale_levels= scheduling_scale_level+1)
    def transport_exp_cost_rule(instance, source, sink, resource, transport, *scale_list):
        return instance.Trans_exp_cost[source, sink, resource, transport, scale_list[:scheduling_scale_level+1]] == \
            trans_cost[transport]*distance_dict[(source, sink)]*instance.Trans_exp[source, sink, resource, transport, scale_list[:scheduling_scale_level+1]]
    instance.transport_exp_cost_constraint = Constraint(instance.sources, instance.sinks, instance.resources_trans, instance.transports, *scales, rule=transport_exp_cost_rule, doc='import of resource from sink to source')
    constraint_latex_render(transport_exp_cost_rule)
    return instance.transport_exp_cost_constraint

def transport_imp_cost_constraint(instance:ConcreteModel, scheduling_scale_level: int= 0, trans_cost:dict = {}, distance_dict:dict = {}) -> Constraint:
    scales = scale_list(instance= instance, scale_levels= scheduling_scale_level+1)
    def transport_imp_cost_rule(instance, sink, source, resource, transport, *scale_list):
        return instance.Trans_imp_cost[sink, source, resource, transport, scale_list[:scheduling_scale_level+1]] == \
            trans_cost[transport]*distance_dict[(source, sink)]*instance.Trans_imp[sink, source, resource, transport, scale_list[:scheduling_scale_level+1]]
    instance.transport_imp_cost_constraint = Constraint(instance.sinks, instance.sources, instance.resources_trans, instance.transports, *scales, rule=transport_imp_cost_rule, doc='import of resource from sink to source')
    constraint_latex_render(transport_imp_cost_rule)
    return instance.transport_imp_cost_constraint

# *-------------------------Transport costing constraints--------------------------

def transport_cost_constraint(instance:ConcreteModel, scheduling_scale_level:int = 0):
    scales = scale_list(instance= instance, scale_levels= scheduling_scale_level+1)
    def transport_cost_rule(instance, transport, *scale_list):
        return instance.Trans_cost[transport, scale_list[:scheduling_scale_level+1]] == \
            sum(instance.Trans_imp_cost[sink, source, resource, transport, scale_list[:scheduling_scale_level+1]] + \
                instance.Trans_exp_cost[source, sink, resource, transport, scale_list[:scheduling_scale_level+1]] \
                    for sink, source, resource in product(instance.sinks, instance.sources, instance.resources_trans))
    instance.transport_cost_constraint = Constraint(instance.transports, *scales, rule = transport_cost_rule, doc = 'total transport cost')
    constraint_latex_render(transport_cost_rule)
    return instance.transport_cost_constraint

def transport_cost_network_constraint(instance:ConcreteModel, network_scale_level:int = 0):
    scales = scale_list(instance= instance, scale_levels = network_scale_level+1) 
    scale_iter = scale_tuple(instance= instance, scale_levels = instance.scales.__len__())
    def transport_cost_network_rule(instance, transport, *scale_list):
        return instance.Trans_cost_network[transport, scale_list] == sum(instance.Trans_cost[transport, scale_] for scale_ in scale_iter)
    instance.transport_cost_network_constraint = Constraint(instance.transports, *scales, rule = transport_cost_network_rule, doc = 'total transport cost across scale')
    constraint_latex_render(transport_cost_network_rule)
    return instance.transport_cost_network_constraint


    

# *-------------------------Location scale mass balance calculation constraints--------------------------

def location_production_constraint(instance:ConcreteModel, cluster_wt:dict, network_scale_level:int=0) -> Constraint:
    """Determines total production capacity utilization at location

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: location_production_constraint
    """
    
    scales = scale_list(instance= instance, scale_levels = network_scale_level+1) 
    scale_iter = scale_tuple(instance= instance, scale_levels = instance.scales.__len__())
    def location_production_rule(instance, location, process, *scale_list):
        if cluster_wt is not None:
            return instance.P_location[location, process, scale_list] == sum(cluster_wt[scale_]*instance.P[location, process, scale_] for scale_ in  scale_iter)
        else:
            return instance.P_location[location, process, scale_list] == sum(instance.P[location, process, scale_] for scale_ in  scale_iter)         
    instance.location_production_constraint = Constraint(instance.locations, instance.processes, *scales, rule = location_production_rule, doc = 'total production at location')
    constraint_latex_render(location_production_rule)
    return instance.location_production_constraint

def location_discharge_constraint(instance:ConcreteModel, cluster_wt:dict, network_scale_level:int=0) -> Constraint:
    """Determines total resource discharged/sold at locations in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: location_discharge_constraint
    """
    scales = scale_list(instance= instance, scale_levels = network_scale_level+1) 
    scale_iter = scale_tuple(instance= instance, scale_levels = instance.scales.__len__())
    def location_discharge_rule(instance, location, resource, *scale_list):
        if cluster_wt is not None:
            return instance.S_location[location, resource, scale_list] == sum(cluster_wt[scale_]*instance.S[location, resource, scale_] for scale_ in  scale_iter)
        else:
            return instance.S_location[location, resource, scale_list] == sum(instance.S[location, resource, scale_] for scale_ in  scale_iter)
    instance.location_discharge_constraint = Constraint(instance.locations, instance.resources_sell, *scales, rule = location_discharge_rule, doc = 'total discharge at location')
    constraint_latex_render(location_discharge_rule)
    return instance.location_discharge_constraint

def location_consumption_constraint(instance:ConcreteModel, cluster_wt:dict, network_scale_level:int=0) -> Constraint:
    """Determines total resource consumed at locations in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: location_consumption_constraint
    """
    scales = scale_list(instance= instance, scale_levels = network_scale_level+1) 
    scale_iter = scale_tuple(instance= instance, scale_levels = instance.scales.__len__())
    def location_consumption_rule(instance, location, resource, *scale_list):
        if cluster_wt is not None:
            return instance.C_location[location, resource, scale_list] == sum(cluster_wt[scale_]*instance.C[location, resource, scale_] for scale_ in  scale_iter)
        else:
            return instance.C_location[location, resource, scale_list] == sum(instance.C[location, resource, scale_] for scale_ in  scale_iter)
    instance.location_consumption_constraint = Constraint(instance.locations, instance.resources_purch, *scales, rule = location_consumption_rule, doc = 'total consumption at location')
    constraint_latex_render(location_consumption_rule)
    return instance.location_consumption_constraint


def location_purchase_constraint(instance:ConcreteModel, cluster_wt:dict, network_scale_level:int=0) -> Constraint:
    """Determines total resource purchase expenditure at locations in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: location_purchase_constraint
    """
    scales = scale_list(instance= instance, scale_levels = network_scale_level+1) 
    scale_iter = scale_tuple(instance= instance, scale_levels = instance.scales.__len__())
    def location_purchase_rule(instance, location, resource, *scale_list):
        if cluster_wt is not None:
            return instance.B_location[location, resource, scale_list] == sum(cluster_wt[scale_]*instance.B[location, resource, scale_] for scale_ in  scale_iter)
        else:
            return instance.B_location[location, resource, scale_list] == sum(instance.B[location, resource, scale_] for scale_ in  scale_iter)
    instance.location_purchase_constraint = Constraint(instance.locations, instance.resources_purch, *scales, rule = location_purchase_rule, doc = 'total purchase at location')
    constraint_latex_render(location_purchase_rule)
    return instance.location_purchase_constraint


# *-------------------------Network scale mass balance calculation constraints--------------------------

def network_production_constraint(instance:ConcreteModel, network_scale_level:int=0) -> Constraint:
    """Determines total production utilization across network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: network_production_constraint
    """
    scales = scale_list(instance= instance, scale_levels = network_scale_level+1) 
    def network_production_rule(instance, process, *scale_list):
        return instance.P_network[process, scale_list] == sum(instance.P_location[location_, process, scale_list] for location_ in instance.locations) 
    instance.network_production_constraint = Constraint(instance.processes, *scales, rule = network_production_rule, doc = 'total production from network')
    constraint_latex_render(network_production_rule)
    return instance.network_production_constraint

def network_discharge_constraint(instance:ConcreteModel, network_scale_level:int=0) -> Constraint:
    """Determines total resource discharged across network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: network_discharge_constraint
    """
    scales = scale_list(instance= instance, scale_levels = network_scale_level+1) 
    def network_discharge_rule(instance, resource, *scale_list):
        return instance.S_network[resource, scale_list] == sum(instance.S_location[location_, resource, scale_list] for location_ in instance.locations) 
    instance.network_discharge_constraint = Constraint(instance.resources_sell, *scales, rule = network_discharge_rule, doc = 'total discharge from network')
    constraint_latex_render(network_discharge_rule)
    return instance.network_discharge_constraint

def network_consumption_constraint(instance:ConcreteModel, network_scale_level:int=0) -> Constraint:
    """Determines total resource consumed across network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: network_consumption_constraint
    """
    scales = scale_list(instance= instance, scale_levels = network_scale_level+1) 
    def network_consumption_rule(instance, resource, *scale_list):
        return instance.C_network[resource, scale_list] == sum(instance.C_location[location_, resource, scale_list] for location_ in instance.locations) 
    instance.network_consumption_constraint = Constraint(instance.resources_purch, *scales, rule = network_consumption_rule, doc = 'total consumption from network')
    constraint_latex_render(network_consumption_rule)
    return instance.network_consumption_constraint


def network_purchase_constraint(instance:ConcreteModel, network_scale_level:int=0) -> Constraint:
    """Determines total purchase expenditure on resource across network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: network_purchase_constraint
    """
    scales = scale_list(instance= instance, scale_levels = network_scale_level+1) 
    def network_purchase_rule(instance, resource, *scale_list):
        return instance.B_network[resource, scale_list] == sum(instance.B_location[location_, resource, scale_list] for location_ in instance.locations) 
    instance.network_purchase_constraint = Constraint(instance.resources_purch, *scales, rule = network_purchase_rule, doc = 'total purchase from network')
    constraint_latex_render(network_purchase_rule)
    return instance.network_purchase_constraint

# *-------------------------Process costing constraints--------------------------------------

def process_capex_constraint(instance:ConcreteModel, capex_dict:dict, network_scale_level:int=0, annualization_factor:float = 1) -> Constraint:
    """Capital expenditure for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        capex_dict (dict): capex at location #TODO
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        annualization_factor (float, optional): Annual depreciation of asset. Defaults to 1.

    Returns:
        Constraint: process_capex_constraint
    """
    scales = scale_list(instance= instance, scale_levels = network_scale_level+1) 
    def process_capex_rule(instance, location, process, *scale_list):
        return instance.Capex_process[location, process, scale_list] == annualization_factor*capex_dict[process]*instance.Cap_P[location, process, scale_list]
    instance.process_capex_constraint = Constraint(instance.locations, instance.processes, *scales, rule = process_capex_rule, doc = 'total purchase from network')
    constraint_latex_render(process_capex_rule)
    return instance.process_capex_constraint

def delta_cap_location_constraint(instance:ConcreteModel, network_scale_level:int=0) -> Constraint:
    scales = scale_list(instance= instance, scale_levels = network_scale_level+1) 
    scale_iter = scale_tuple(instance= instance, scale_levels = instance.scales.__len__())
    def delta_cap_location_rule(instance, location, process, *scale_list):
        return instance.Delta_Cap_P_location[location, process, scale_list] == sum(instance.Delta_Cap_P[location, process, scale_] for scale_ in scale_iter)
    instance.delta_cap_location_constraint = Constraint(instance.locations, instance.processes_varying, *scales, rule = delta_cap_location_rule, doc = 'total transport cost across scale')
    constraint_latex_render(delta_cap_location_rule)
    return instance.delta_cap_location_constraint

def delta_cap_network_constraint(instance:ConcreteModel, network_scale_level:int=0) -> Constraint:
    scales = scale_list(instance= instance, scale_levels = network_scale_level+1) 
    def delta_cap_network_rule(instance, process, *scale_list):
        return instance.Delta_Cap_P_network[process, scale_list] == sum(instance.Delta_Cap_P_location[location_, process, scale_list] for location_ in instance.locations)
    instance.delta_cap_network_constraint = Constraint(instance.processes_varying, *scales, rule = delta_cap_network_rule, doc = 'total transport cost across scale')
    constraint_latex_render(delta_cap_network_rule)
    return instance.delta_cap_network_constraint

def process_fopex_constraint(instance:ConcreteModel, fopex_dict:dict, network_scale_level:int=0, annualization_factor:float = 1) -> Constraint:
    """Fixed operational expenditure for each process at location in network
    Args:
        instance (ConcreteModel): pyomo instance
        fopex_dict (dict): fixed opex at location #TODO
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        annualization_factor (float, optional): Annual depreciation of asset. Defaults to 1.

    Returns:
        Constraint: process_fopex_constraint
    """
    scales = scale_list(instance= instance, scale_levels = network_scale_level+1) 
    def process_fopex_rule(instance, location, process, *scale_list):
        return instance.Fopex_process[location, process, scale_list] == annualization_factor*fopex_dict[process]*instance.Cap_P[location, process, scale_list]
    instance.process_fopex_constraint = Constraint(instance.locations, instance.processes, *scales, rule = process_fopex_rule, doc = 'total purchase from network')
    constraint_latex_render(process_fopex_rule)
    return instance.process_fopex_constraint

def process_vopex_constraint(instance:ConcreteModel, vopex_dict:dict, network_scale_level:int=0, annualization_factor:float = 1) -> Constraint:
    """Fixed operational expenditure for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: process_vopex_constraint
    """
    scales = scale_list(instance= instance, scale_levels = network_scale_level+1) 
    def process_vopex_rule(instance, location, process, *scale_list):
        return instance.Vopex_process[location, process, scale_list] == annualization_factor*vopex_dict[process]*instance.P_location[location, process, scale_list]
    instance.process_vopex_constraint = Constraint(instance.locations, instance.processes, *scales, rule = process_vopex_rule, doc = 'total purchase from network')
    constraint_latex_render(process_vopex_rule)
    return instance.process_vopex_constraint


# *-------------------------Location costing constraints--------------------------------------

def location_capex_constraint(instance:ConcreteModel, network_scale_level:int=0) -> Constraint:
    """Capital expenditure for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: location_capex_constraint
    """
    scales = scale_list(instance= instance, scale_levels = network_scale_level+1) 
    def location_capex_rule(instance, location, *scale_list):
        return instance.Capex_location[location, scale_list] == sum(instance.Capex_process[location, process_, scale_list] for process_ in instance.processes)
    instance.location_capex_constraint = Constraint(instance.locations, *scales, rule = location_capex_rule, doc = 'total purchase from network')
    constraint_latex_render(location_capex_rule)
    return instance.location_capex_constraint

def location_fopex_constraint(instance:ConcreteModel, network_scale_level:int=0) -> Constraint:
    """Fixed operational expenditure for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: location_fopex_constraint
    """
    scales = scale_list(instance= instance, scale_levels = network_scale_level+1) 
    def location_fopex_rule(instance, location, *scale_list):
        return instance.Fopex_location[location, scale_list] == sum(instance.Fopex_process[location, process_, scale_list] for process_ in instance.processes)
    instance.location_fopex_constraint = Constraint(instance.locations, *scales, rule = location_fopex_rule, doc = 'total purchase from network')
    constraint_latex_render(location_fopex_rule)
    return instance.location_fopex_constraint

def location_vopex_constraint(instance:ConcreteModel, network_scale_level:int=0) -> Constraint:
    """Fixed operational expenditure for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: location_vopex_constraint
    """
    scales = scale_list(instance= instance, scale_levels = network_scale_level+1) 
    def location_vopex_rule(instance, location, *scale_list):
        return instance.Vopex_location[location, scale_list] == sum(instance.Vopex_process[location, process_, scale_list] for process_ in instance.processes)
    instance.location_vopex_constraint = Constraint(instance.locations, *scales, rule = location_vopex_rule, doc = 'total purchase from network')
    constraint_latex_render(location_vopex_rule)
    return instance.location_vopex_constraint


# *-------------------------Network costing constraints--------------------------------------

def network_capex_constraint(instance:ConcreteModel, network_scale_level:int=0) -> Constraint:
    """Capital expenditure for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: network_capex_constraint
    """
    scales = scale_list(instance= instance, scale_levels = network_scale_level+1) 
    def network_capex_rule(instance, *scale_list):
        return instance.Capex_network[scale_list] == sum(instance.Capex_location[location_, scale_list] for location_ in instance.locations) 
    instance.network_capex_constraint = Constraint(*scales, rule = network_capex_rule, doc = 'total purchase from network')
    constraint_latex_render(network_capex_rule)
    return instance.network_capex_constraint

def network_vopex_constraint(instance:ConcreteModel, network_scale_level:int=0) -> Constraint:
    """Variable operational expenditure for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: network_vopex_constraint
    """
    scales = scale_list(instance= instance, scale_levels = network_scale_level+1) 
    def network_vopex_rule(instance, *scale_list):
        return instance.Vopex_network[scale_list] == sum(instance.Vopex_location[location_, scale_list] for location_ in instance.locations) 
    instance.network_vopex_constraint = Constraint(*scales, rule = network_vopex_rule, doc = 'total purchase from network')
    constraint_latex_render(network_vopex_rule)
    return instance.network_vopex_constraint


def network_fopex_constraint(instance:ConcreteModel, network_scale_level:int=0) -> Constraint:
    """Fixed operational for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        
    Returns:
        Constraint: network_fopex_constraint
    """
    scales = scale_list(instance= instance, scale_levels = network_scale_level+1) 
    def network_fopex_rule(instance, *scale_list):
        return instance.Fopex_network[scale_list] == sum(instance.Fopex_location[location_, scale_list] for location_ in instance.locations) 
    instance.network_fopex_constraint = Constraint(*scales, rule = network_fopex_rule, doc = 'total purchase from network')
    constraint_latex_render(network_fopex_rule)
    return instance.network_fopex_constraint

# *-------------------------Demand constraint--------------------------------------

def demand_constraint(instance:ConcreteModel, demand: Union[dict,float], demand_scale_level:int= 0, scheduling_scale_level:int= 0) -> Constraint:
    """Ensures that demand for resource is met at chosen temporal scale

    Args:
        instance (ConcreteModel): pyomo instance
        demand_scale_level (int, optional): scale of demand decisions. Defaults to 0.
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.
        demand_dict (dict, optional): demand at location. Defaults to {}.

    Returns:
        Constraint: demand_constraint
    """
    # scales = scale_list(instance= instance, scale_levels = demand_scale_level+1) 
    scales = scale_list(instance= instance, scale_levels = instance.scales.__len__())
    scale_iter = scale_tuple(instance= instance, scale_levels = scheduling_scale_level+1)
    def demand_rule(instance, location, resource, *scale_list):
        if type(demand[location][list(demand[location])[0]]) == float:
            return sum(instance.S[location, resource_, scale_list[:scheduling_scale_level+1]] for \
                    resource_ in instance.resources_demand) == demand[location][scale_list[:demand_scale_level+1]] 
        else:
            return sum(instance.S[location, resource, scale_] for scale_ in scale_iter if scale_[:scheduling_scale_level+1] == scale_list)\
                            == demand[location][scale_list[:demand_scale_level+1]][resource]   
                 
    if len(instance.locations) > 1:    
        instance.demand_constraint = Constraint(instance.sinks, instance.resources_demand, *scales, rule = demand_rule, doc = 'specific demand for resources')
    else:                 
         instance.demand_constraint = Constraint(instance.locations, instance.resources_demand, *scales, rule = demand_rule, doc = 'specific demand for resources')        
    constraint_latex_render(demand_rule)
    return instance.demand_constraint

# *-------------------------Nexus constraints--------------------------------------

def process_land_constraint(instance:ConcreteModel, land_dict:dict, network_scale_level:int=0) -> Constraint:
    """Land required for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        land_dict (dict): land required at location
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        
    Returns:
        Constraint: process_land_constraint
    """
    scales = scale_list(instance= instance, scale_levels = network_scale_level+1) 
    def process_land_rule(instance, location, process, *scale_list):
        return instance.Land_process[location, process, scale_list] == land_dict[process]*instance.Cap_P[location, process, scale_list]
    instance.process_land_constraint = Constraint(instance.locations, instance.processes, *scales, rule = process_land_rule, doc = 'land required for process')
    constraint_latex_render(process_land_rule)
    return instance.process_land_constraint

def location_land_constraint(instance:ConcreteModel, network_scale_level:int=0) -> Constraint:
    """Land required at each location in network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        
    Returns:
        Constraint: location_land_constraint
    """
    scales = scale_list(instance= instance, scale_levels = network_scale_level+1) 
    def location_land_rule(instance, location, *scale_list):
        return instance.Land_location[location, scale_list] == sum(instance.Land_process[location, process_, scale_list] for process_ in instance.processes)
    instance.location_land_constraint = Constraint(instance.locations, *scales, rule = location_land_rule, doc = 'land required for process')
    constraint_latex_render(location_land_rule)
    return instance.location_land_constraint

def network_land_constraint(instance:ConcreteModel, network_scale_level:int=0) -> Constraint:
    """Land required by network

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        
    Returns:
        Constraint: network_land_constraint
    """
    scales = scale_list(instance= instance, scale_levels = network_scale_level+1) 
    def network_land_rule(instance, *scale_list):
        return instance.Land_network[scale_list] == sum(instance.Land_location[location_, scale_list] for location_ in instance.locations)
    instance.network_land_constraint = Constraint(*scales, rule = network_land_rule, doc = 'land required for process')
    constraint_latex_render(network_land_rule)
    return instance.network_land_constraint

# def carbon_emission_constraint(instance.ConcreteModel, network_scale_level:int=0) -> Constraint:
    
#     scales = scale_list(instance= instance, scale_levels = network_scale_level+1) 
#     def network_land_rule(instance, *scale_list):
#         return instance.carbon_network[scale_list] == instance.Land_location[location_, scale_list] for location_ in instance.locations)
#     instance.network_land_constraint = Constraint(*scales, rule = network_land_rule, doc = 'land required for process')
#     constraint_latex_render(network_land_rule)
#     return instance.network_land_constraint


# *-------------------------Uncertainty analysis constraints------------------------------------

def uncertain_nameplate_production_constraint(instance: ConcreteModel, network_scale_level:int = 0, scheduling_scale_level:int= 0) -> Constraint:
    """Determines production capacity utilization of facilities at location in network and capacity of facilities 
    with uncertain capacility available for utilization

    Args:
        instance (ConcreteModel): pyomo instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.

    Returns:
        Constraint: uncertain_nameplate_production_constraint
    """
    scales = scale_list(instance= instance, scale_levels = instance.scales.__len__())
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


   
def uncertain_resource_purchase_constraint(instance: ConcreteModel, price:dict = {},  loc_res_dict:dict = {}, scheduling_scale_level:int= 0, expenditure_scale_level:int= 0) -> Constraint:
    """Determines expenditure on resource at location in network at the scheduling/expenditure scale
    with uncertainty in resource proce

    Args:
        instance (ConcreteModel): pyomo instance
        price (dict, optional): base price of resource. Defaults to {}.
        loc_res_dict (dict, optional): storage facilities for resource available at location. Defaults to {}.
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.
        expenditure_scale_level (int, optional): scale of expenditure decisions. Defaults to 0.

    Returns:
        Constraint: uncertain_resource_purchase_constraint
    """
    scales = scale_list(instance= instance, scale_levels = instance.scales.__len__())
    def uncertain_resource_purchase_rule(instance, location, resource, *scale_list):
        if resource in instance.resources_varying.intersection(loc_res_dict[location]):
            return instance.B[location, resource, scale_list[:scheduling_scale_level+1]] == price[location][resource]*\
                instance.C[location, resource, scale_list[:scheduling_scale_level+1]]*instance.Delta_Cost_R[location, resource, scale_list[:scheduling_scale_level+1]] 
        else:
            if resource in instance.resources_purch.intersection(loc_res_dict[location]):
                return instance.B[location, resource, scale_list[:scheduling_scale_level+1]] == price[location][resource]*instance.C[location, resource, scale_list[:scheduling_scale_level+1]]      
            else:
                return instance.B[location, resource, scale_list[:scheduling_scale_level+1]] == 0     
    constraint_latex_render(uncertain_resource_purchase_rule)
    instance.uncertain_resource_purchase_constraint = Constraint(instance.locations, instance.resources_purch, *scales, rule=uncertain_resource_purchase_rule, doc='expenditure on purchase of resource')
    return instance.uncertain_resource_purchase_constraint


# %%
