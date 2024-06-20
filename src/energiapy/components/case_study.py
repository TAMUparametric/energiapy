"""Case data class
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2023, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "MIT"
__version__ = "1.0.8"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from dataclasses import dataclass
from typing import Union, Set, Dict, Tuple
import copy
from warnings import warn

from .scenario import Scenario
from .process import Process
from .resource import Resource
from .location import Location
from .result import Result, Results

from ..model.formulate import formulate as formulate_casestudy
from ..model.solve import solve as solve_casestudy
from ..model.formulate import Objective, ModelClass
from ..model.constraints.constraints import Constraints
from pyomo.environ import ConcreteModel


@dataclass
class CaseStudy:
    """Case studies are a collection of scenarios that can be analyzed 

    Args:
        name (str): name of the case study
        scenarios: Can be a list of scenarios generated apriori or a single scenario that you want to vary
        vary (str, optional): if single scenario, what needs to be varied. e.g. demand. Defaults to None
        vary_as (str, optional): what values to assign while varying. Should be a list of values to take. Defaults to None
        formulations_dict (dict, optional): dictionary with pyomo instances. Defaults to None 
        results_dict (Results, optional): Results type object, has multiple Result objects embedded. Defaults to None

    """
    name: str
    scenarios: Union[list, Scenario] = None
    vary: str = None
    vary_as: list = None
    formulations: dict = None
    results: Results = None

    def __post_init__(self):

        if isinstance(self.scenarios, Scenario) is True:
            scenario_list = []
            counter = 0
            for i in self.vary_as:
                scenario = copy.deepcopy(self.scenarios)
                if self.vary == 'demand':
                    scenario.demand = i
                scenario.name = scenario.name + str(counter + 1)
                scenario_list.append(scenario)
                counter += 1
            self.scenarios = scenario_list

    def formulate(self, constraints: Set[Constraints] = None, objective: Objective = None,
                  write_lpfile: bool = False, gwp: float = None, land_restriction: float = None,
                  gwp_reduction_pct: float = None, model_class: ModelClass = ModelClass.MIP, objective_resource: Resource = None,
                  inventory_zero: Dict[Location, Dict[Tuple[Process, Resource], float]] = None) -> Dict[str, ConcreteModel]:
        """formulates a pyomo instance for all scenarios in a case study


        Args:
            scenario (Scenario): scenario to formulate model over
            constraints (Set[Constraints], optional): constraints to include. Defaults to None
            objective (Objective, optional): objective. Defaults to None
            write_lpfile (bool, False): write out a .LP file. Uses scenario.name as name.
            gwp (float, optional): _description_. Defaults to None.
            land_restriction (float, optional): restrict land usage. Defaults to 10**9.
            gwp_reduction_pct (float, optional): percentage reduction in gwp required. Defaults to None.
            model_class (ModelClass, optional): class of model [MIP, mpLP]. Defaults to ModelClass.MIP
            objective_resource (Resource, None): resource to feature in objective for maximization and such
            inventory_zero (Dict[Location, Dict[Tuple[Process, Resource], float]], optional): inventory at the start of the scheduling horizon. Defaults to None.

        Returns:
            Dict[str, ConcreteModel]: Dictionary of pyomo instance
        """

        self.formulations = {i.name: formulate_casestudy(scenario=i, constraints=constraints, objective=objective,
                                                         write_lpfile=write_lpfile, gwp=gwp, land_restriction=land_restriction,
                                                         gwp_reduction_pct=gwp_reduction_pct, model_class=model_class, objective_resource=objective_resource,
                                                         inventory_zero=inventory_zero) for i in self.scenarios}

        return self.formulations

    def solve(self, solver: str, interface: str = 'pyomo', saveformat: str = None, print_solversteps: bool = True, log: bool = False, get_duals: bool = False) -> Dict[str, Result]:
        """solves all the instances in the case study

        Args:
            solver (str): solver, e.g. gurobi, BARON, ANTIGONE, CPLEX
            interface (str, optional): Currently, pyomo's native and gams is available. Defaults to 'pyomo'.
            saveformat (str, optional): .pkl, .json, .txt. Defaults to None.
            print_solversteps (bool, optional):. Defaults to True.
            log (bool, optional): Log nearbounds in case of optimal, and violations if infeasible. Defaults to False
            get_duals (bool, optional): get and save the duals in the results

        Returns:
            Result: result type object
        """
        if self.formulations is None:
            warn('Instances have not been formulated yet, use .formulate() first')

        instances = list(self.formulations.values())
        names = list(self.formulations.keys())

        self.results = Results(name=self.name + '_results', results={names[i]: solve_casestudy(instance=instances[i], scenario=self.scenarios[i],
                                                                                               solver=solver, name=names[
                                                                                                   i], interface=interface, saveformat=saveformat,
                                                                                               print_solversteps=print_solversteps, log=log, get_duals=get_duals) for i in range(len(names))})

        return self.results
