#%%
"""pyomo_solve
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "0.0.1"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from pyomo.environ import ConcreteModel, SolverFactory
from ..components.result import Result
from ..components.scenario import Scenario

def solve(instance:ConcreteModel, solver:str, name:str, scenario:Scenario = None, saveformat:str = None, tee:bool = True) -> Result:
    output = SolverFactory(solver, solver_io= 'python').solve(instance, tee = True)
    
    if scenario is None:
        components_dict = {}
    else:
        components_dict = {
            'transports': {i.name: i.__dict__ for i in scenario.transport_set},
            'processes': {i.name: i.__dict__ for i in scenario.process_set},  
            'resources': {i.name: i.__dict__ for i in scenario.resource_set},   
            'materials': {i.name: i.__dict__ for i in scenario.material_set},    
            'locations': {i.name: i.__dict__ for i in scenario.location_set}
            }
    results_dict ={
        'LB': output['Problem'][0]['Lower bound'], 
        'UB': output['Problem'][0]['Upper bound'],
        'n_cons': output['Problem'][0]['Number of constraints'],
        'n_vars': output['Problem'][0]['Number of variables'],
        'n_binvars': output['Problem'][0]['Number of binary variables'],
        'n_intvars': output['Problem'][0]['Number of integer variables'],
        'n_convars': output['Problem'][0]['Number of continuous variables'],
        'n_nonzero': output['Problem'][0]['Number of nonzeros'],
        'P': instance.P.extract_values(),   
        'B': instance.B.extract_values(),       
        'C': instance.C.extract_values(),        
        'S': instance.S.extract_values(),        
        'Inv': instance.Inv.extract_values(),        
        'Imp': instance.Imp.extract_values(),        
        'Exp': instance.Exp.extract_values(),        
        'Fopex_process': instance.Fopex_process.extract_values(),       
        'Vopex_process': instance.Vopex_process.extract_values(),       
        'Capex_process': instance.Capex_process.extract_values(),       
        'Fopex_location': instance.Fopex_location.extract_values(),        
        'Vopex_location': instance.Vopex_location.extract_values(),        
        'Capex_location': instance.Capex_location.extract_values(),           
        'Fopex_network': instance.Fopex_network.extract_values(),        
        'Vopex_network': instance.Vopex_network.extract_values(),        
        'Capex_network': instance.Capex_network.extract_values(),    
        'Cap_P': instance.Cap_P.extract_values(),    
        'Cap_S': instance.Cap_S.extract_values(),    
        'X_P': instance.X_P.extract_values(),    
        'X_S': instance.X_S.extract_values(),    
        'Trans_imp': instance.Trans_imp.extract_values(),    
        'Trans_exp': instance.Trans_exp.extract_values(),    
        'P_location': instance.P_location.extract_values(),    
        'B_location': instance.B_location.extract_values(),        
        'C_location': instance.C_location.extract_values(),        
        'S_location': instance.S_location.extract_values(),  
        'P_network': instance.P_network.extract_values(),    
        'B_network': instance.B_network.extract_values(),        
        'C_network': instance.C_network.extract_values(),        
        'S_network': instance.S_network.extract_values(),  
        'Trans_cost': instance.Trans_cost.extract_values(),
        'Trans_cost_network': instance.Trans_cost_network.extract_values(),
        'cost_objective': instance.uncertainty_cost_objective(),   
        'Delta_Cost_R': instance.Delta_Cost_R.extract_values(),        
        'Delta_Cap_P': instance.Delta_Cap_P.extract_values(),  
        'Delta_Cap_P_location': instance.Delta_Cap_P_location.extract_values(),  
        'Delta_Cap_P_network': instance.Delta_Cap_P_network.extract_values(),  
        }
    
    results = Result(name= name, components = components_dict, output= results_dict)

    if saveformat is not None:
        results.saveoutputs(name + saveformat)
    
    return results




# %%
