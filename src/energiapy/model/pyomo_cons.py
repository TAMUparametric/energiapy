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
        if resource in instance.resources_store.intersection(loc_res_dict[location]):
            return instance.Inv[location, resource, scale_list[:scheduling_scale_level+1]] <= instance.Cap_S[location, resource, scale_list[:network_scale_level+1]]
        else:
            return instance.Inv[location, resource, scale_list[:scheduling_scale_level+1]] <= 0
    instance.nameplate_inventory_constraint = Constraint(
        instance.locations, instance.resources, *scales, rule=nameplate_inventory_rule, doc='nameplate inventory capacity constraint')
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
        instance.locations, instance.resources, *scales, rule=resource_consumption_rule, doc='resource consumption')
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
    instance.resource_purchase_constraint = Constraint(instance.locations, instance.resources, *scales, rule=resource_purchase_rule, doc='expenditure on purchase of resource')
    return instance.resource_purchase_constraint

def resource_discharge_constraint(instance: ConcreteModel, scheduling_scale_level:int= 0) -> Constraint:
    """Determines discharge/sale of resource at location in network 

    Args:
        instance (ConcreteModel): pyomo instance
        scheduling_scale_level (int, optional): scale of scheduling decisions. Defaults to 0.

    Returns:
        Constraint: resource_discharge_constraint
    """
    scales = scale_list(instance= instance, scale_levels = instance.scales.__len__())
    def resource_discharge_rule(instance, location, resource, *scale_list):
        if resource in instance.resource_nosell:
            return instance.S[location, resource, scale_list[:scheduling_scale_level+1]] == 0
    instance.resource_discharge_constraint = Constraint(instance.locations, instance.resource_nosell, *scales, rule=resource_discharge_rule, doc='restrict discharge of non marketable resources')
    constraint_latex_render(resource_discharge_rule)
    return instance.resource_discharge_constraint

def test_cycle(instance: ConcreteModel,  scheduling_scale_level:int= 0) -> Constraint:
    """TEST CONSTRAINT
    """
    scales = scale_list(instance= instance, scale_levels = instance.scales.__len__())
    scale_iter = scale_tuple(instance= instance, scale_levels = instance.scales.__len__())
    def test_cycle_rule(instance, location, resource, *scale_list):
        if scale_list[:scheduling_scale_level+1] != scale_iter[0]:
            return instance.Inv[location, resource, scale_list[:scheduling_scale_level+1]] - instance.Inv[location, resource, scale_iter[scale_iter.index(scale_list[:scheduling_scale_level+1]) -1]] == 0
        else:
            return instance.Inv[location, resource, scale_list[:scheduling_scale_level+1]] == 0
    instance.test_cycle_cons = Constraint(instance.locations, instance.resource_nosell, *scales, rule=test_cycle_rule, doc='restrict discharge of non marketable resources')
    constraint_latex_render(test_cycle)
    return instance.test_cycle_cons

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


# *-------------------------Location scale mass balance calculation constraints--------------------------

def location_production_constraint(instance:ConcreteModel, network_scale_level:int=0) -> Constraint:
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
        return instance.P_location[location, process, scale_list] == \
            sum(instance.P[location, process, scale_] for scale_ in  scale_iter)
    instance.location_production_constraint = Constraint(instance.locations, instance.processes, *scales, rule = location_production_rule, doc = 'total production at location')
    constraint_latex_render(location_production_rule)
    return instance.location_production_constraint

def location_discharge_constraint(instance:ConcreteModel, network_scale_level:int=0) -> Constraint:
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
        return instance.S_location[location, resource, scale_list] == \
            sum(instance.S[location, resource, scale_] for scale_ in  scale_iter)
    instance.location_discharge_constraint = Constraint(instance.locations, instance.resources, *scales, rule = location_discharge_rule, doc = 'total discharge at location')
    constraint_latex_render(location_discharge_rule)
    return instance.location_discharge_constraint

def location_consumption_constraint(instance:ConcreteModel, network_scale_level:int=0) -> Constraint:
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
        return instance.C_location[location, resource, scale_list] == \
            sum(instance.C[location, resource, scale_] for scale_ in  scale_iter)
    instance.location_consumption_constraint = Constraint(instance.locations, instance.resources, *scales, rule = location_consumption_rule, doc = 'total consumption at location')
    constraint_latex_render(location_consumption_rule)
    return instance.location_consumption_constraint


def location_purchase_constraint(instance:ConcreteModel, network_scale_level:int=0) -> Constraint:
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
        return instance.B_location[location, resource, scale_list] == \
            sum(instance.B[location, resource, scale_] for scale_ in  scale_iter)
    instance.location_purchase_constraint = Constraint(instance.locations, instance.resources, *scales, rule = location_purchase_rule, doc = 'total purchase at location')
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
    instance.network_discharge_constraint = Constraint(instance.resources, *scales, rule = network_discharge_rule, doc = 'total discharge from network')
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
    instance.network_consumption_constraint = Constraint(instance.resources, *scales, rule = network_consumption_rule, doc = 'total consumption from network')
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
    instance.network_purchase_constraint = Constraint(instance.resources, *scales, rule = network_purchase_rule, doc = 'total purchase from network')
    constraint_latex_render(network_purchase_rule)
    return instance.network_purchase_constraint

# *-------------------------Loction costing constraints--------------------------------------

def location_capex_constraint(instance:ConcreteModel, capex_dict:dict, network_scale_level:int=0, annualization_factor:float = 1) -> Constraint:
    """Capital expenditure for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        capex_dict (dict): capex at location #TODO
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        annualization_factor (float, optional): Annual depreciation of asset. Defaults to 1.

    Returns:
        Constraint: location_capex_constraint
    """
    scales = scale_list(instance= instance, scale_levels = network_scale_level+1) 
    def location_capex_rule(instance, location, process, *scale_list):
        return instance.Capex_location[location, process, scale_list] == annualization_factor*capex_dict[process]*instance.Cap_P[location, process, scale_list]
    instance.location_capex_constraint = Constraint(instance.locations, instance.processes, *scales, rule = location_capex_rule, doc = 'total purchase from network')
    constraint_latex_render(location_capex_rule)
    return instance.location_capex_constraint

def location_fopex_constraint(instance:ConcreteModel, fopex_dict:dict, network_scale_level:int=0, annualization_factor:float = 1) -> Constraint:
    """Fixed operational expenditure for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        fopex_dict (dict): fixed opex at location #TODO
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        annualization_factor (float, optional): Annual depreciation of asset. Defaults to 1.

    Returns:
        Constraint: location_fopex_constraint
    """
    scales = scale_list(instance= instance, scale_levels = network_scale_level+1) 
    def location_fopex_rule(instance, location, process, *scale_list):
        return instance.Fopex_location[location, process, scale_list] == annualization_factor*fopex_dict[process]*instance.Cap_P[location, process, scale_list]
    instance.location_fopex_constraint = Constraint(instance.locations, instance.processes, *scales, rule = location_fopex_rule, doc = 'total purchase from network')
    constraint_latex_render(location_fopex_rule)
    return instance.location_fopex_constraint

def location_vopex_constraint(instance:ConcreteModel, vopex_dict:dict, network_scale_level:int=0, annualization_factor:float = 1) -> Constraint:
    """Fixed operational expenditure for each process at location in network

    Args:
        instance (ConcreteModel): pyomo instance
        vopex_dict (dict): variable opex at location #TODO
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.
        annualization_factor (float, optional): Annual depreciation of asset. Defaults to 1.

    Returns:
        Constraint: location_vopex_constraint
    """
    scales = scale_list(instance= instance, scale_levels = network_scale_level+1) 
    def location_vopex_rule(instance, location, process, *scale_list):
        return instance.Vopex_location[location, process, scale_list] == annualization_factor*vopex_dict[process]*instance.P_location[location, process, scale_list]
    instance.location_vopex_constraint = Constraint(instance.locations, instance.processes, *scales, rule = location_vopex_rule, doc = 'total purchase from network')
    constraint_latex_render(location_vopex_rule)
    return instance.location_vopex_constraint

# *-------------------------Demand constraints--------------------------------------

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
    instance.uncertain_resource_purchase_constraint = Constraint(instance.locations, instance.resources, *scales, rule=uncertain_resource_purchase_rule, doc='expenditure on purchase of resource')
    return instance.uncertain_resource_purchase_constraint


# %%
