# %%
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

import logging

from pyomo.environ import ConcreteModel, Constraint, Objective, SolverFactory, Var
from pyomo.util.infeasible import (
    log_close_to_bounds,
    log_infeasible_bounds,
    log_infeasible_constraints,
)

from ..components.result import Result
from ..components.scenario import Scenario


def solve(instance: ConcreteModel, solver: str, name: str, scenario: Scenario = None, saveformat: str = None, print_solversteps: bool = True) -> Result:
    output = SolverFactory(solver, solver_io='python').solve(
        instance, tee=print_solversteps)

    if scenario is None:
        components_dict = {}
    else:
        components_dict = {
            'processes': {i.name: i.__dict__ for i in scenario.process_set},
            'resources': {i.name: i.__dict__ for i in scenario.resource_set},
            'materials': {i.name: i.__dict__ for i in scenario.material_set},
            'locations': {i.name: i.__dict__ for i in scenario.location_set},
            'transports': {}
        }

    if len(instance.locations) > 1:
        components_dict['transports'] = {
            i.name: i.__dict__ for i in scenario.transport_set}

    solution_dict = {
        'termination': str(output['Solver'][0]['Termination condition']),
        'LB': output['Problem'][0]['Lower bound'],
        'UB': output['Problem'][0]['Upper bound'],
        'n_cons': output['Problem'][0]['Number of constraints'],
        'n_vars': output['Problem'][0]['Number of variables'],
        'n_binvars': output['Problem'][0]['Number of binary variables'],
        'n_intvars': output['Problem'][0]['Number of integer variables'],
        'n_convars': output['Problem'][0]['Number of continuous variables'],
        'n_nonzero': output['Problem'][0]['Number of nonzeros']
    }

    if solution_dict['termination'] == 'optimal':

        model_vars = instance.component_map(ctype=Var)
        vars_dict = {i: model_vars[i].extract_values()
                     for i in model_vars.keys()}

        model_obj = instance.component_map(ctype=Objective)
        obj_dict = {'objective': model_obj[i]() for i in model_obj.keys()}

        output_dict = {**solution_dict, **vars_dict, **obj_dict}

        model_cons = [i for i in instance.component_objects()
                      if i.ctype == Constraint]

        if solution_dict['n_binvars'] > 0:
            duals_dict = {}
        else:
            index_dict = {c: list(c.index_set()) for c in model_cons}
            duals_dict = {cons.name: {index: instance.dual[cons[index]] for index
                                      in index_dict[cons]} for cons in model_cons}

        logging.basicConfig(
            filename=f"{scenario.name}_nearbound.log", encoding='utf-8', level=logging.INFO)
        log_close_to_bounds(instance)

    else:
        output_dict = solution_dict
        duals_dict = {}

        logging.basicConfig(
            filename=f"{scenario.name}_infeasible.log", encoding='utf-8', level=logging.INFO)
        log_infeasible_bounds(instance)
        log_infeasible_constraints(instance)
        log_close_to_bounds(instance)

    results = Result(name=name, components=components_dict,
                     output=output_dict, duals=duals_dict)

    if saveformat is not None:
        results.saveoutputs(name + saveformat)

    return results

# %%


# %
