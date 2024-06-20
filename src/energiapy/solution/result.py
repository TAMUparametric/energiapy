import json
import pickle
from dataclasses import dataclass
from typing import Dict
import uuid

@dataclass
class Result:
    """Results from solving a Scenario

    Args:
       name (str): name of the material, short ones are better to deal with.
       components (dict): input data relating to components
       output (dict): results from analysis
       model_elements (dict): model sets, variables, constraints, objective
       duals (dict): duals if not MIP.
       solve_time (float): solution time
       cost_summary (dict): summary of the contributing costs

    """
    components: dict
    output: dict
    model_elements: dict
    duals: dict
    name: str = None 
    
    def __post_init__(self):
        
        if self.name is None:
            warn(f'{self.name}: random name has been set, this can be cumbersome')
            self.name = f"Result_{uuid.uuid4().hex}"

    def saveoutputs(self, file_name: str):
        """Saves output with provide name.

        Args:
            file_name (str): Give a name to the file you want to save the results in. Be sure to mention extension [.pkl, .json, .txt]
        """
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

    def fetch_components(self, component_type: str, condition: tuple = None) -> set:
        """fetches components that meet a specific condition

        Args:
            component_type (str): type of component: processses, resources, locations, materials, transports
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

        Examples:

            results.fetch_components(component_type= 'processes', condition= ('capex', 'ge', 20 ))
            results.fetch_components(component_type= 'resources', condition= ('sell', True ))
        """
        component_set = set(self.__dict__['components'][component_type].keys())

        if condition is None:
            return component_set

        else:
            if isinstance(condition[1], (bool, str)) and (condition[1] not in ['eq', 'ge', 'le', 'g', 'l']):
                specific_component_set = {i for i in self.components[component_type].keys()
                                          if self.components[component_type][i][condition[0]] == condition[1]}

            elif condition[1] == 'eq':
                specific_component_set = {i for i in self.components[component_type].keys()
                                          if self.components[component_type][i][condition[0]] == condition[2]}
            elif condition[1] == 'ge':
                specific_component_set = {i for i in self.components[component_type].keys()
                                          if self.components[component_type][i][condition[0]] >= condition[2]}
            elif condition[1] == 'le':
                specific_component_set = {i for i in self.components[component_type].keys()
                                          if self.components[component_type][i][condition[0]] <= condition[2]}
            elif condition[1] == 'l':
                specific_component_set = {i for i in self.components[component_type].keys()
                                          if self.components[component_type][i][condition[0]] < condition[2]}
            elif condition[1] == 'g':
                specific_component_set = {i for i in self.components[component_type].keys()
                                          if self.components[component_type][i][condition[0]] > condition[2]}
            else:
                specific_component_set = {}
            return specific_component_set

    def divide_by_objective(self, var: str, index: tuple):
        """divides variable at index

        Args:
            var (str): variable name
            index (tuple): index for variable as tuple
        Returns:
            float: value
        """
        value = self.output[var][index]/self.output['objective']
        return value

    def divide_objective_by(self, var: str, index: tuple):
        """divides variable at index

        Args:
            var (str): variable name
            index (tuple): index for variable as tuple
        Returns:
            float: value
        """
        value = self.output['objective']/self.output[var][index]
        return value

    def get_varindex(self, var: str):
        """gives the index of variable

        Args:
            var (str): variable name

        Returns:
            list: list of tuple indices
        """
        return list(self.output[var].keys())

    def model_summary(self):
        """Prints a summary of the model with number of variables of different types and constraints.
        """
        print(f"SUMMARY:\n\
            number of constraints: {self.output['n_cons']}\n\
            number of variables: {self.output['n_vars']}\n\
            number of binary variables: {self.output['n_binvars']}\n\
            number of integer variables: {self.output['n_intvars']}\n\
            number of continuous variables: {self.output['n_convars']}")

    def cost_summary(self):
        """Makes a summary of contributing costs
        """

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name


@dataclass
class Results:
    """Contains multiple Result objects
    Args:
        name: name of the results object, inherits from CaseStudy
        results: dictionary of Result objects. 
    """
    name: str
    results: Dict[str, Result]

    # capex = instance.Capex_total
    # vopex = instance.Vopex_total
    # fopex = instance.Vopex_total
    # incidental = instance.Incidental_total
    # storage_cost = instance.Inv_cost_total
    # cost_purch = instance.B_total
    # land_cost = instance.Land_cost_total
    # credit = instance.Credit_total
    # else:
    #     credit = 0

    # if len(instance.locations) > 1:
    #     cost_trans_capex = instance.Capex_transport_total
    #     cost_trans_vopex = instance.Vopex_transport_total
    #     cost_trans_fopex = instance.Fopex_transport_total
    # else:
    #     cost_trans_capex = 0
    #     cost_trans_vopex = 0
    #     cost_trans_fopex = 0
