"""pyomo emission constraints
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
from ...utils.latex_utils import constraint_latex_render
from ...utils.scale_utils import scale_list
from ...utils.scale_utils import scale_pyomo_set
from ...utils.scale_utils import scale_tuple
from ...components.location import Location
from itertools import product
from typing import Union
from enum import Enum, auto



def carbon_emission_location_constraint(instance: ConcreteModel, network_scale_level:int=0) -> Constraint:
    """Determines the total CO2_Vent at each location

    Args:
        instance (ConcreteModel): pyomo model instance
        network_scale_level (int, optional): scale of network decisions. Defaults to 0.

    Returns:
        Constraint: carbon_emission_location_constraint
    """
    scales = scale_list(instance= instance, scale_levels = network_scale_level+1)
    def carbon_emission_location_rule(instance, location, *scale_list):
        return instance.carbon_emission_location[location, scale_list] == instance.S_location[location, 'CO2_Vent', scale_list] 
    instance.carbon_emission_location_constraint = Constraint(instance.locations, *scales, rule = carbon_emission_location_rule, doc = 'carbon_emission_location_process')
    
    constraint_latex_render(carbon_emission_location_rule)
    return instance.carbon_emission_location_constraint

def carbon_emission_constraint(instance: ConcreteModel, carbon_bound:float,  network_scale_level:int=0, carbon_reduction_percentage:float = 0.0) -> Constraint:
    """Determines the total network-wide CO2_Vent 

    Args:
        instance (ConcreteModel): pyomo model instance
        carbon_bound (float): bound for network carbon emission
        network_scale_level (int, optional):  scale of network decisions. Defaults to 0.
        carbon_reduction_percentage (float, optional): percentage reduction required. Defaults to 0.0.

    Returns:
        Constraint: carbon_emission_constraint
    """
    scales = scale_list(instance= instance, scale_levels = network_scale_level+1)
    def carbon_emission_rule(instance, location, *scale_list):
        return instance.S_location[location, 'CO2_Vent', scale_list] <= (100.0 - carbon_reduction_percentage)*carbon_bound/100.0
    instance.carbon_emission_constraint = Constraint(instance.locations, *scales, rule = carbon_emission_rule, doc = 'carbon_emission_process')
    constraint_latex_render(carbon_emission_rule)
    return instance.carbon_emission_constraint


def global_warming_potential_process_constraint(instance: ConcreteModel, process_gwp_dict: dict, network_scale_level:int=0):
    scales = scale_list(instance= instance, scale_levels= network_scale_level+1)
    
    def global_warming_potential_process_rule(instance, location, process,  *scale_list):
        return instance.global_warming_potential_process[location, process, scale_list] == process_gwp_dict[location][process]*instance.Cap_P[location, process, scale_list]
    instance.global_warming_potential_process_constraint = Constraint(instance.locations, instance.processes, *scales, rule = global_warming_potential_process_rule, doc= 'global warming potential for the each process' )
    constraint_latex_render(global_warming_potential_process_rule)
    return instance.global_warming_potential_process_constraint

#TODO - Fix this, this needs some work
def global_warming_potential_material_constraint(instance: ConcreteModel, material_gwp_dict: dict, process_material_dict: dict, network_scale_level:int=0):
    scales = scale_list(instance= instance, scale_levels= network_scale_level+1)
    
    def global_warming_potential_material_rule(instance, location, process,  *scale_list):
        return instance.global_warming_potential_material[location, process, scale_list] == \
            sum(process_material_dict[process][material]*material_gwp_dict[location][material] for material in process_material_dict[process].keys()) *\
                instance.Cap_P[location, process, scale_list] 
    instance.global_warming_potential_material_constraint = Constraint(instance.locations, instance.processes_materials, *scales, rule = global_warming_potential_material_rule, doc= 'global warming potential for the each material' )
    constraint_latex_render(global_warming_potential_material_rule)
    return instance.global_warming_potential_material_constraint

def global_warming_potential_resource_constraint(instance: ConcreteModel, resource_gwp_dict: dict, network_scale_level:int=0):
    scales = scale_list(instance= instance, scale_levels= network_scale_level+1)
    
    def global_warming_potential_resource_rule(instance, location, resource,  *scale_list):
        return instance.global_warming_potential_resource[location, resource, scale_list] == resource_gwp_dict[location][resource]*instance.C_location[location, resource, scale_list]
    instance.global_warming_potential_resource_constraint = Constraint(instance.locations, instance.resources_purch, *scales, rule = global_warming_potential_resource_rule, doc= 'global warming potential for the each resource' )
    constraint_latex_render(global_warming_potential_resource_rule)
    return instance.global_warming_potential_resource_constraint


def global_warming_potential_location_constraint(instance: ConcreteModel, network_scale_level:int=0):
    scales = scale_list(instance= instance, scale_levels= network_scale_level+1)
    
    def global_warming_potential_location_rule(instance, location, *scale_list):
        gwp_process =  sum(instance.global_warming_potential_process[location, process_, scale_list] for process_ in instance.processes)
        gwp_resource = sum(instance.global_warming_potential_resource[location, resource_, scale_list] for resource_ in instance.resources_purch)
        gwp_material = sum(instance.global_warming_potential_material[location, material_, scale_list] for material_ in instance.processes_materials)
        
        return instance.global_warming_potential_location[location, scale_list] == gwp_process + gwp_resource + gwp_material
    instance.global_warming_potential_location_constraint = Constraint(instance.locations, *scales, rule = global_warming_potential_location_rule, doc= 'global warming potential for the each location' )
    constraint_latex_render(global_warming_potential_location_rule)
    return instance.global_warming_potential_location_constraint

def global_warming_potential_network_constraint(instance: ConcreteModel, network_scale_level:int=0):
    scales = scale_list(instance= instance, scale_levels= network_scale_level+1)
    
    def global_warming_potential_network_rule(instance, *scale_list):
        return instance.global_warming_potential_network[scale_list] == \
            sum(instance.global_warming_potential_location[location_, scale_list] for location_ in instance.locations)
    instance.global_warming_potential_network_constraint = Constraint(*scales, rule = global_warming_potential_network_rule, doc= 'global warming potential for the whole network' )
    constraint_latex_render(global_warming_potential_network_rule)
    return instance.global_warming_potential_network_constraint

def global_warming_potential_network_reduction_constraint(instance: ConcreteModel, network_scale_level:int=0, gwp_reduction_pct:float= 0, gwp:float = 0):
    scales = scale_list(instance= instance, scale_levels= network_scale_level+1)
    
    def global_warming_potential_network_reduction_rule(instance, *scale_list):
        return instance.global_warming_potential_network[scale_list] <= gwp*(1 - gwp_reduction_pct/100)
    instance.global_warming_potential_network_reduction_constraint = Constraint(*scales, rule = global_warming_potential_network_reduction_rule, doc= 'global warming potential for the whole network' )
    constraint_latex_render(global_warming_potential_network_reduction_rule)
    return instance.global_warming_potential_network_reduction_constraint



def carbon_emission_network_constraint(instance: ConcreteModel, network_scale_level:int=0) -> Constraint:
    scales = scale_list(instance= instance, scale_levels = network_scale_level+1)
    def carbon_emission_network_rule(instance, *scale_list):
        return instance.carbon_emission_network[scale_list] == sum(instance.carbon_emission_location[location_, scale_list] for location_ in instance.locations)
    instance.carbon_emission_network_constraint = Constraint(*scales, rule = carbon_emission_network_rule, doc = 'carbon_emission_network_process')
    constraint_latex_render(carbon_emission_network_rule)
    return instance.carbon_emission_network_constraint

