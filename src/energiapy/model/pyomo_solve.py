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

from pyomo.environ import ConcreteModel, SolverFactory, Var, Objective
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
    solution_dict ={
        'LB': output['Problem'][0]['Lower bound'], 
        'UB': output['Problem'][0]['Upper bound'],
        'n_cons': output['Problem'][0]['Number of constraints'],
        'n_vars': output['Problem'][0]['Number of variables'],
        'n_binvars': output['Problem'][0]['Number of binary variables'],
        'n_intvars': output['Problem'][0]['Number of integer variables'],
        'n_convars': output['Problem'][0]['Number of continuous variables'],
        'n_nonzero': output['Problem'][0]['Number of nonzeros'] 
        }
    
    model_vars = instance.component_map(ctype = Var)    
    vars_dict = {i: model_vars[i].extract_values() for i in model_vars.keys()}  
    
    model_obj = instance.component_map(ctype = Objective)
    obj_dict = {i: model_obj[i]() for i in model_obj.keys()}  
    
    results_dict = {**solution_dict, **vars_dict, **obj_dict}

    results = Result(name= name, components = components_dict, output= results_dict)

    if saveformat is not None:
        results.saveoutputs(name + saveformat)
    
    return results




# %%
