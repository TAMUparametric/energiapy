"""Result data class  
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "0.0.1"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from dataclasses import dataclass
from pyomo.environ import ConcreteModel
from pyomo.opt import SolverResults
from ..components.scenario import Scenario
import json
import pickle




@dataclass
class Result:
    """Result data class object
    
    Args:
 |      name (str): ID for the resource
 |      instance (Concrete Model): pyomo instance.
 |      output(SolverResults): pyomo solver outputs
    """
    name:str
    instance: ConcreteModel = None
    output: SolverResults = None
    if self.output is not None:
        def __post_init__(self):
            self.LB = self.output['Problem'][0]['Lower bound'] 
            self.UB = self.output['Problem'][0]['Upper bound']
            self.n_cons = self.output['Problem'][0]['Number of constraints']
            self.n_vars = self.output['Problem'][0]['Number of variables']
            self.n_binvars = self.output['Problem'][0]['Number of binary variables']
            self.n_intvars = self.output['Problem'][0]['Number of integer variables']
            self.n_convars = self.output['Problem'][0]['Number of continuous variables']
            self.n_nonzero = self.output['Problem'][0]['Number of nonzeros']
            self.P = self.instance.P.extract_values()    
            self.B = self.instance.B.extract_values()        
            self.C = self.instance.C.extract_values()        
            self.S = self.instance.S.extract_values()        
            self.Inv = self.instance.Inv.extract_values()        
            self.Imp = self.instance.Imp.extract_values()        
            self.Exp = self.instance.Exp.extract_values()        
            self.Fopex_process = self.instance.Fopex_process.extract_values()        
            self.Vopex_process = self.instance.Vopex_process.extract_values()        
            self.Capex_process = self.instance.Capex_process.extract_values()        
            self.Fopex_location = self.instance.Fopex_location.extract_values()        
            self.Vopex_location = self.instance.Vopex_location.extract_values()        
            self.Capex_location = self.instance.Capex_location.extract_values()           
            self.Fopex_network = self.instance.Fopex_network.extract_values()        
            self.Vopex_network = self.instance.Vopex_network.extract_values()        
            self.Capex_network = self.instance.Capex_network.extract_values()    
            self.Cap_P = self.instance.Cap_P.extract_values()    
            self.Cap_S = self.instance.Cap_S.extract_values()    
            self.X_P = self.instance.X_P.extract_values()    
            self.X_S = self.instance.X_S.extract_values()    
            self.Trans_imp = self.instance.Trans_imp.extract_values()    
            self.Trans_exp = self.instance.Trans_exp.extract_values()    
            self.P_location = self.instance.P_location.extract_values()    
            self.B_location = self.instance.B_location.extract_values()        
            self.C_location = self.instance.C_location.extract_values()        
            self.S_location = self.instance.S_location.extract_values()  
            self.P_network = self.instance.P_network.extract_values()    
            self.B_network = self.instance.B_network.extract_values()        
            self.C_network = self.instance.C_network.extract_values()        
            self.S_network = self.instance.S_network.extract_values()  
            self.Trans_cost = self.instance.Trans_cost.extract_values()
            self.Trans_cost_network = self.instance.Trans_cost_network.extract_values()
            self.cost_objective = self.instance.uncertainty_cost_objective()   
            self.Delta_Cost_R = self.instance.Delta_Cost_R.extract_values()        
            self.Delta_Cap_P = self.instance.Delta_Cap_P.extract_values()  
            self.Delta_Cap_P_location = self.instance.Delta_Cap_P_location.extract_values()  
            self.Delta_Cap_P_network = self.instance.Delta_Cap_P_network.extract_values()  

    def saveoutputs(self, file_name:str):
        data = self.__dict__
        del data['instance']
        del data['output']

        if '.pkl' in file_name:
            with open(file_name, "wb") as f:
                pickle.dump(data, f)
                f.close()
        elif '.json' in file_name:
            with open(file_name, 'w') as f:
                json.dump(data, f)

        elif '.txt' in file_name:
            with open(file_name, "w") as f:
                f.write(str(data))
                f.close()
        return

            
    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name


@dataclass
class Loaded_Results(Result):
    """Result data class object loaded from saved files
    
    Args:
 |      name (str): ID for the resource
 |      instance (Concrete Model): pyomo instance.
 |      output(SolverResults): pyomo solver outputs
    """
    def __init__(name:str, instance:ConcreteModel = None,  output: SolverResults = None, **kwargs):
        super(Loaded_Results, self).__init__(**kwargs)
        self.name = name