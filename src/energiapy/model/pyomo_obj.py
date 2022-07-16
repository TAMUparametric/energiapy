"""pyomo objective
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "0.0.1"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from pyomo.environ import ConcreteModel, Obj 

# def nameplate_production_constraint(instance: ConcreteModel, location_set:set, network_scale_level:int = 0, scheduling_scale_level:int= 0) -> Constraint:
    
#     scale_level = max(network_scale_level, scheduling_scale_level)
#     scales = scale_list(instance= instance, scale_level = scale_level)
#     capacity_factor = {location.name: location.capacity_factor for location in location_set}
#     print(scales)
    
#     #%%% use intersection of processes from location object and capacity factor processes 
#     def nameplate_production_rule(instance, location, process, *scale_list):
        
#         if process in instance.processes_varying:
            
#             return instance.P[location, process, scale_list[:scheduling_scale_level+1]] <= \
#                 capacity_factor[location][process][scale_list[:scheduling_scale_level+1]]*instance.Cap_P[location, process, scale_list[:network_scale_level+1]]
#         else:
            
#             return instance.P[location, process, scale_list[:scheduling_scale_level+1]] <= instance.Cap_P[location, process, scale_list[:network_scale_level+1]]
        
#     instance.nameplate_production_constraint = Constraint(
#         instance.locations, instance.processes, *scales, rule=nameplate_production_rule, doc='nameplate production capacity constraint')
    
#     constraint_latex_render(nameplate_production_rule)
    
#     return instance.nameplate_production_constraint




# def min_system_cost(instance:ConcreteModel, location_set:set):

