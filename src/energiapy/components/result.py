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
    """
    Object with resource data
    
    Args:
        name (str): ID for the resource
        label (str, optional): name of the resource. Defaults to ''.
        consumption_max (float, optional): Maximum allowed resource consumption in time period [unit/h]. Defaults to 0.
        loss (float, optional): Amount of resource lost in time period [h]. Defaults to 0.
        revenue (float, optional): Amount earned through sale of resource [$/unit]. Defaults to 0.
        price (float, optional): Purchase cost of unit [$/unit]. Defaults to 0.
        mile (float, optional): mileage offered by resource [mile/unit]. Defaults to 0.
        store_max (float, optional): Maximum storage capacity increase in a year. Defaults to 0.
        store_min (float, optional): Minimum storage capacity increase in a year. Defaults to 0.
        sell (bool, optional): True if resource can be discharged. Defaults to False.
        demand (bool, optional): True, if the process has to meet set demand. Defaults to False.
        basis (str, optional): Base unit for the resource. Defaults to 'unit'.
        block (str, optional): Assign a block for categorization. Defaults to None.
        varying (bool, optional): If the cost of resource is varying/uncertain. Defaults to False.
        citation (str, optional): Add citations for data sources. Defaults to 'citation needed'.
    """
    
    name: str
    instance: ConcreteModel 
    result: SolverResults
    
    
    def __post_init__(self):
        self.LB = self.result['Problem'][0]['Lower bound']
        self.UB = self.result['Problem'][0]['Upper bound']
        self.n_cons = self.result['Problem'][0]['Number of constraints']
        self.n_vars = self.result['Problem'][0]['Number of variables']
        self.n_binvars = self.result['Problem'][0]['Number of binary variables']
        self.n_intvars = self.result['Problem'][0]['Number of integer variables']
        self.n_convars = self.result['Problem'][0]['Number of continuous variables']
        self.n_nonzero = self.result['Problem'][0]['Number of nonzeros']
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
        
    
    def saveresults(self, file_name:str):
        data = self.__dict__
        del data['instance']
        del data['result']

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

