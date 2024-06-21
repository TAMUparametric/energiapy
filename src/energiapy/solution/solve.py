import logging
import time
from warnings import warn

from ppopt.mp_solvers.solve_mpqp import mpqp_algorithm, solve_mpqp
from ppopt.mplp_program import MPLP_Program
from pyomo.environ import (ConcreteModel, Constraint, Objective, Set,
                           SolverFactory, Var)
from pyomo.util.infeasible import (log_close_to_bounds, log_infeasible_bounds,
                                   log_infeasible_constraints)

from ..solution.result import Result


def solve(scenario, solver: str, name: str, instance: ConcreteModel = None, matrix: dict = None, interface: str = 'pyomo', saveformat: str = None, print_solversteps: bool = True, log: bool = False, get_duals: bool = False) -> Result:
    """solves a model instance, scenario needs to be provided

    Args:
        solver (str): solver, e.g. gurobi, BARON, ANTIGONE, CPLEX
        name (str): name for results
        instance (ConcreteModel, optional): Pyomo instance. Defaults to None. 
        matrix (dict, optional): generated from formulate (ModelClass.MPLP). Defaults to None
        interface (str, optional): Currently, pyomo, native, and GAMS is available. Defaults to 'pyomo'.
        scenario (Scenario, optional): scenario. Defaults to None.
        saveformat (str, optional): .pkl, .json, .txt. Defaults to None.
        print_solversteps (bool, optional):. Defaults to True.
        log (bool, optional): Log nearbounds in case of optimal, and violations if infeasible. Defaults to False
        get_duals (bool, optional): get and save the duals in the results 

    Returns:
        Result: result type object
    """
    start = time.time()
    if interface == 'native':
        if solver == 'ppopt':
            prog = MPLP_Program(matrix['A'], matrix['b'], matrix['c'], matrix['H'],
                                matrix['CRa'], matrix['CRb'], matrix['F'], equality_indices=list(range(matrix['no_eq_cons'])))
            prog.solver.solvers['lp'] = 'gurobi'
            # prog.warnings()
            prog.display_warnings()
            # prog.process_constraints()
            results = solve_mpqp(prog, mpqp_algorithm.combinatorial)
    else:
        if interface == 'pyomo':
            output = SolverFactory(solver, solver_io='python').solve(
                instance, tee=print_solversteps)
            time_sol = output['Solver'][0]['Wallclock time']

        if interface == 'GAMS':
            warn('Ensure GAMS is installed on system and PATH is set')
            output = SolverFactory('gams').solve(
                instance, solver=solver, tee=print_solversteps)
            time_sol = output.SolverFactory.time

        print()
        print(f'The model took {time_sol} seconds to solve')
        print()

        if scenario is None:
            components_dict = {}
        else:
            components_dict = {
                'processes': {i.name: i.__dict__ for i in scenario.process_set},
                'resources': {i.name: i.__dict__ for i in scenario.resource_set},
                'materials': {i.name: i.__dict__ for i in scenario.material_set},
                'locations': {i.name: i.__dict__ for i in scenario.location_set},
                'transports': {},
            }

        if len(instance.locations) > 1:
            components_dict['transports'] = {
                i.name: i.__dict__ for i in scenario.transport_set}

        solution_dict = {
            'termination': str(output['Solver'][0]['Termination condition']),
            'solution_time': time_sol,
            'LB': output['Problem'][0]['Lower bound'],
            'UB': output['Problem'][0]['Upper bound'],
            'n_cons': output['Problem'][0]['Number of constraints'],
            'n_vars': output['Problem'][0]['Number of variables'],
            'n_binvars': output['Problem'][0]['Number of binary variables'],
            'n_intvars': output['Problem'][0]['Number of integer variables'],
            'n_convars': output['Problem'][0]['Number of continuous variables'],
            'n_nonzero': output['Problem'][0]['Number of nonzeros'],
        }

        model_sets = [i for i in instance.component_objects()
                      if i.ctype == Set]

        model_vars = [i for i in instance.component_objects()
                      if i.ctype == Var]

        model_cons = [i for i in instance.component_objects()
                      if i.ctype == Constraint]

        model_obj = [i for i in instance.component_objects()
                     if i.ctype == Objective]

        sets_list = [str(i) for i in model_sets if 'index' not in str(i)]

        vars_list = list(map(str, model_vars))

        cons_list = list(map(str, model_cons))

        obj = str(list(model_obj)[0])

        model_dict = {'sets': sets_list, 'variables': vars_list,
                      'constraints': cons_list, 'objective': obj}

        if solution_dict['termination'] == 'optimal':

            vars_cmap = instance.component_map(ctype=Var)

            vars_dict = {i: vars_cmap[i].extract_values()
                         for i in vars_cmap.keys()}
            vars_list = list(vars_dict.keys())

            obj_cmap = instance.component_map(ctype=Objective)
            obj_dict = {'objective': obj_cmap[i]() for i in obj_cmap.keys()}

            output_dict = {**solution_dict, **vars_dict, **obj_dict}

            if get_duals is True:
                if solution_dict['n_binvars'] is not None:
                    if solution_dict['n_binvars'] > 0:
                        duals_dict = dict()
                    else:
                        start_duals = time.time()
                        index_dict = {c: list(c.index_set())
                                      for c in model_cons}
                        duals_dict = {cons.name: {index: instance.dual[cons[index]] for index
                                                  in index_dict[cons] if index in cons.keys()} for cons in model_cons}
                        end_duals = time.time()
                        time_duals = end_duals - start_duals
                        print()
                        print(
                            f'It took {time_duals} seconds to generate duals')
                        print()

                else:
                    duals_dict = dict()
            else:
                duals_dict = dict()

            if log is True:
                start_log = time.time()
                logging.basicConfig(
                    filename=f"{scenario.name}_nearbound.log", encoding='utf-8', level=logging.INFO)
                log_close_to_bounds(instance)
                end_log = time.time()
                time_log = end_log - start_log
                print()
                print(
                    f'It took {time_log} seconds to create a log')
                print()
        else:
            output_dict = solution_dict
            duals_dict = {}

            if log is True:
                start_log = time.time()
                logging.basicConfig(
                    filename=f"{scenario.name}_infeasible.log", encoding='utf-8', level=logging.INFO)
                log_infeasible_bounds(instance)
                log_infeasible_constraints(instance)
                log_close_to_bounds(instance)
                end_log = time.time()
                time_log = end_log - start_log
                print()
                print(
                    f'It took {time_log} seconds to create a log')
                print()

        results = Result(name=name, components=components_dict,
                         output=output_dict, model_elements=model_dict, duals=duals_dict)

        if saveformat is not None:
            start_save = time.time()
            results.saveoutputs(name + saveformat)
            end_save = time.time()
            time_save = end_save - start_save
            print()
            print(
                f'It took {time_save} seconds to save the results as a {saveformat} file')
            print()
    end = time.time()
    time_total = end - start
    print()
    print(f'Total time needed to generate result was {time_total} seconds')
    print()
    return results
