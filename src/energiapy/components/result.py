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
       name (str): ID for the resource
       components (dict): input data relating to components
       output (dict): results from analysis
    """
    name:str
    components: dict
    output: dict

    def saveoutputs(self, file_name:str):
        data = self.__dict__

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

    def fetch_components(self, component_type:str) -> set:
        component_set = set(self.__dict__['components'][component_type].keys())
        return component_set     
            
    
    def fetch_components_specific(self, component_type:str, condition:tuple) -> set:
        """fetches components that meet a specific condition

        Args:
            component_type (str): type of component: processs, resources, locations, materials, transports 
            condition (tuple): condition to be met
            For bool:
            condition = ('attribute', True))
            For str:
            condition = ('attribute', str))
            For numeric:
            condition = ('attribute', '*', numeric))
            * - can be 'eq', 'ge', 'le', 'g', 'l'

        Returns:
            set: set meeting condition
        """
        component_set = self.fetch_components(component_type)
        if (type(condition[1]) == bool or str) and (condition[1] not in ['eq', 'ge', 'le', 'g', 'l']) :
            specific_component_set = {i for i in self.components[component_type].keys()\
                if self.components[component_type][i][condition[0]] == condition[1]}
        
        elif condition[1] == 'eq':
            specific_component_set = {i for i in self.components[component_type].keys()\
                if self.components[component_type][i][condition[0]] == condition[2]}
        elif condition[1] == 'ge':
            specific_component_set = {i for i in self.components[component_type].keys()\
                if self.components[component_type][i][condition[0]] >= condition[2]}
        elif condition[1] == 'le':
            specific_component_set = {i for i in self.components[component_type].keys()\
                if self.components[component_type][i][condition[0]] <= condition[2]}
        elif condition[1] == 'l':
            specific_component_set = {i for i in self.components[component_type].keys()\
                if self.components[component_type][i][condition[0]] < condition[2]}
        elif condition[1] == 'g':
            specific_component_set = {i for i in self.components[component_type].keys()\
                if self.components[component_type][i][condition[0]] > condition[2]}
        else:
            specific_component_set = {}
        return specific_component_set

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name


