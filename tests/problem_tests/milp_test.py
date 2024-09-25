from tests.test_fixtures import single_location_milp_variability_cost
from src.energiapy.model.solve import solve
from src.energiapy.model.formulate import formulate
import copy

# Function to round all numerical values to 3 decimal places


def round_values(d):
    if isinstance(d, dict):
        for key, value in d.items():
            if isinstance(value, (float, int)):
                # Round the numerical value to 3 decimal places
                d[key] = round(value, 3)
            elif isinstance(value, dict):
                round_values(value)
    elif isinstance(d, list):
        for i, item in enumerate(d):
            if isinstance(item, (float, int)):
                # Round the numerical value to 3 decimal places
                d[i] = round(item, 3)
            elif isinstance(item, (dict, list)):
                round_values(item)


def test_results_single_location_milp_variability_cost(single_location_milp_variability_cost):
    results = solve(scenario=single_location_milp_variability_cost[0],
                    instance=single_location_milp_variability_cost[1], solver='gurobi', name='MILP')
    results_rounded = copy.deepcopy(results.output)
    round_values(results_rounded)

    assert (results_rounded == {'termination': 'optimal',
                                'LB': 47423.333,
                                'UB': 47423.333,
                                'n_cons': 176,
                                'n_vars': 159,
                                'n_binvars': 6,
                                'n_intvars': 6,
                                'n_convars': 147,
                                'n_nonzero': 399,
                                'P': {('location', 'process_certain_capacity', 0, 0): 25.0,
                                      ('location', 'process_certain_capacity', 0, 1): 25.0,
                                      ('location', 'process_certain_capacity', 0, 2): 25.0,
                                      ('location', 'process_certain_capacity', 0, 3): 25.0,
                                      ('location', 'process_deterministic_capacity', 0, 0): 41.667,
                                      ('location', 'process_deterministic_capacity', 0, 1): 20.833,
                                      ('location', 'process_deterministic_capacity', 0, 2): 33.333,
                                      ('location', 'process_deterministic_capacity', 0, 3): 10.417,
                                      ('location', 'process_deterministic_capacity2', 0, 0): 0.0,
                                      ('location', 'process_deterministic_capacity2', 0, 1): 0.0,
                                      ('location', 'process_deterministic_capacity2', 0, 2): 0.0,
                                      ('location', 'process_deterministic_capacity2', 0, 3): 0.0,
                                      ('location', 'process_storage', 0, 0): 16.667,
                                      ('location', 'process_storage', 0, 1): 0.0,
                                      ('location', 'process_storage', 0, 2): 8.333,
                                      ('location', 'process_storage', 0, 3): 0.0,
                                      ('location', 'process_storage_discharge', 0, 0): 0.0,
                                      ('location', 'process_storage_discharge', 0, 1): 16.667,
                                      ('location', 'process_storage_discharge', 0, 2): 0.0,
                                      ('location', 'process_storage_discharge', 0, 3): 8.333},
                                'B': {('location', 'resource_certain_availability', 0, 0): 83.333,
                                      ('location', 'resource_certain_availability', 0, 1): 41.667,
                                      ('location', 'resource_certain_availability', 0, 2): 66.667,
                                      ('location', 'resource_certain_availability', 0, 3): 20.833,
                                      ('location', 'resource_deterministic_availability', 0, 0): 62.5,
                                      ('location', 'resource_deterministic_availability', 0, 1): 62.5,
                                      ('location', 'resource_deterministic_availability', 0, 2): 62.5,
                                      ('location', 'resource_deterministic_availability', 0, 3): 62.5,
                                      ('location', 'resource_deterministic_price', 0, 0): 15.625,
                                      ('location', 'resource_deterministic_price', 0, 1): 62.5,
                                      ('location', 'resource_deterministic_price', 0, 2): 31.25,
                                      ('location', 'resource_deterministic_price', 0, 3): 46.875},
                                'C': {('location', 'resource_certain_availability', 0, 0): 41.667,
                                      ('location', 'resource_certain_availability', 0, 1): 20.833,
                                      ('location', 'resource_certain_availability', 0, 2): 33.333,
                                      ('location', 'resource_certain_availability', 0, 3): 10.417,
                                      ('location', 'resource_deterministic_availability', 0, 0): 12.5,
                                      ('location', 'resource_deterministic_availability', 0, 1): 12.5,
                                      ('location', 'resource_deterministic_availability', 0, 2): 12.5,
                                      ('location', 'resource_deterministic_availability', 0, 3): 12.5,
                                      ('location', 'resource_deterministic_price', 0, 0): 6.25,
                                      ('location', 'resource_deterministic_price', 0, 1): 6.25,
                                      ('location', 'resource_deterministic_price', 0, 2): 6.25,
                                      ('location', 'resource_deterministic_price', 0, 3): 6.25},
                                'S': {('location', 'resource_deterministic_demand', 0, 0): 12.5,
                                      ('location', 'resource_deterministic_demand', 0, 1): 25.0,
                                      ('location', 'resource_deterministic_demand', 0, 2): 12.5,
                                      ('location', 'resource_deterministic_demand', 0, 3): 6.25,
                                      ('location', 'resource_deterministic_revenue', 0, 0): 25.0,
                                      ('location', 'resource_deterministic_revenue', 0, 1): 25.0,
                                      ('location', 'resource_deterministic_revenue', 0, 2): 25.0,
                                      ('location', 'resource_deterministic_revenue', 0, 3): 25.0},
                                'R': {('location', 'resource_deterministic_demand', 0, 0): None,
                                      ('location', 'resource_deterministic_demand', 0, 1): None,
                                      ('location', 'resource_deterministic_demand', 0, 2): None,
                                      ('location', 'resource_deterministic_demand', 0, 3): None,
                                      ('location', 'resource_deterministic_revenue', 0, 0): None,
                                      ('location', 'resource_deterministic_revenue', 0, 1): None,
                                      ('location', 'resource_deterministic_revenue', 0, 2): None,
                                      ('location', 'resource_deterministic_revenue', 0, 3): None},
                                'Inv': {('location',
                                         'process_storage_resource_deterministic_demand_stored',
                                         0,
                                         0): 16.667,
                                        ('location',
                                         'process_storage_resource_deterministic_demand_stored',
                                         0,
                                         1): 0.0,
                                        ('location',
                                         'process_storage_resource_deterministic_demand_stored',
                                         0,
                                         2): 8.333,
                                        ('location',
                                         'process_storage_resource_deterministic_demand_stored',
                                         0,
                                         3): 0.0},
                                'P_m': {('location', 'process_deterministic_capacity2', 0, 0, 0): 0.0,
                                        ('location', 'process_deterministic_capacity2', 0, 0, 1): 0.0,
                                        ('location', 'process_deterministic_capacity2', 0, 0, 2): 0.0,
                                        ('location', 'process_deterministic_capacity2', 0, 0, 3): 0.0,
                                        ('location', 'process_certain_capacity', 0, 0, 0): 25.0,
                                        ('location', 'process_certain_capacity', 0, 0, 1): 25.0,
                                        ('location', 'process_certain_capacity', 0, 0, 2): 25.0,
                                        ('location', 'process_certain_capacity', 0, 0, 3): 25.0,
                                        ('location', 'process_deterministic_capacity', 0, 0, 0): 41.667,
                                        ('location', 'process_deterministic_capacity', 0, 0, 1): 20.833,
                                        ('location', 'process_deterministic_capacity', 0, 0, 2): 33.333,
                                        ('location', 'process_deterministic_capacity', 0, 0, 3): 10.417,
                                        ('location', 'process_storage_discharge', 0, 0, 0): 0.0,
                                        ('location', 'process_storage_discharge', 0, 0, 1): 16.667,
                                        ('location', 'process_storage_discharge', 0, 0, 2): 0.0,
                                        ('location', 'process_storage_discharge', 0, 0, 3): 8.333,
                                        ('location', 'process_storage', 0, 0, 0): 16.667,
                                        ('location', 'process_storage', 0, 0, 1): 0.0,
                                        ('location', 'process_storage', 0, 0, 2): 8.333,
                                        ('location', 'process_storage', 0, 0, 3): 0.0},
                                'P_material_m': {},
                                'Cap_P': {('location', 'process_certain_capacity', 0): 25.0,
                                          ('location', 'process_deterministic_capacity', 0): 41.667,
                                          ('location', 'process_deterministic_capacity2', 0): 0.0,
                                          ('location', 'process_storage', 0): 16.667,
                                          ('location', 'process_storage_discharge', 0): 50.0},
                                'Cap_S': {('location',
                                           'process_storage_resource_deterministic_demand_stored',
                                           0): 25.0},
                                'P_location': {('location', 'process_certain_capacity', 0): 100.0,
                                               ('location', 'process_deterministic_capacity', 0): 106.25,
                                               ('location', 'process_deterministic_capacity2', 0): 0.0,
                                               ('location', 'process_storage', 0): 25.0,
                                               ('location', 'process_storage_discharge', 0): 25.0},
                                'P_location_material_m': {},
                                'S_location': {('location', 'resource_deterministic_demand', 0): 56.25,
                                               ('location', 'resource_deterministic_revenue', 0): 100.0},
                                'R_location': {('location', 'resource_deterministic_demand', 0): None,
                                               ('location', 'resource_deterministic_revenue', 0): None},
                                'C_location': {('location', 'resource_certain_availability', 0): 106.25,
                                               ('location', 'resource_deterministic_availability', 0): 50.0,
                                               ('location', 'resource_deterministic_price', 0): 25.0},
                                'B_location': {('location', 'resource_certain_availability', 0): 212.5,
                                               ('location', 'resource_deterministic_availability', 0): 250.0,
                                               ('location', 'resource_deterministic_price', 0): 156.25},
                                'P_network': {('process_certain_capacity', 0): 100.0,
                                              ('process_deterministic_capacity', 0): 106.25,
                                              ('process_deterministic_capacity2', 0): 0.0,
                                              ('process_storage', 0): 25.0,
                                              ('process_storage_discharge', 0): 25.0},
                                'S_network': {('resource_deterministic_demand', 0): 56.25,
                                              ('resource_deterministic_revenue', 0): 100.0},
                                'R_network': {('resource_deterministic_demand', 0): None,
                                              ('resource_deterministic_revenue', 0): None},
                                'C_network': {('resource_certain_availability', 0): 106.25,
                                              ('resource_deterministic_availability', 0): 50.0,
                                              ('resource_deterministic_price', 0): 25.0},
                                'B_network': {('resource_certain_availability', 0): 212.5,
                                              ('resource_deterministic_availability', 0): 250.0,
                                              ('resource_deterministic_price', 0): 156.25},
                                'Fopex_process': {('location', 'process_certain_capacity', 0): 250.0,
                                                  ('location', 'process_deterministic_capacity', 0): 416.667,
                                                  ('location', 'process_deterministic_capacity2', 0): 0.0,
                                                  ('location', 'process_storage', 0): 83.333,
                                                  ('location', 'process_storage_discharge', 0): 0.0},
                                'Vopex_process': {('location', 'process_certain_capacity', 0): 100.0,
                                                  ('location', 'process_deterministic_capacity', 0): 106.25,
                                                  ('location', 'process_deterministic_capacity2', 0): 0.0,
                                                  ('location', 'process_storage', 0): 12.5,
                                                  ('location', 'process_storage_discharge', 0): 0.0},
                                'Capex_process': {('location', 'process_certain_capacity', 0): 2500.0,
                                                  ('location', 'process_deterministic_capacity', 0): 41666.667,
                                                  ('location', 'process_deterministic_capacity2', 0): 0.0,
                                                  ('location', 'process_storage', 0): 1666.667,
                                                  ('location', 'process_storage_discharge', 0): 0.0},
                                'Incidental_process': {('location', 'process_certain_capacity', 0): 0.0,
                                                       ('location', 'process_deterministic_capacity', 0): 0.0,
                                                       ('location', 'process_deterministic_capacity2', 0): 0.0,
                                                       ('location', 'process_storage', 0): 0.0,
                                                       ('location', 'process_storage_discharge', 0): 0.0},
                                'Fopex_location': {('location', 0): 750.0},
                                'Vopex_location': {('location', 0): 218.75},
                                'Capex_location': {('location', 0): 45833.333},
                                'Incidental_location': {('location', 0): 0.0},
                                'Fopex_network': {0: 750.0},
                                'Vopex_network': {0: 218.75},
                                'Capex_network': {0: 45833.333},
                                'Incidental_network': {0: 0.0},
                                'Inv_network': {('location',
                                                 'process_storage_resource_deterministic_demand_stored',
                                                 0): 25.0},
                                'Cost': {None: None},
                                'Inv_cost': {('location',
                                              'process_storage_resource_deterministic_demand_stored',
                                              0): 2.5},
                                'Inv_cost_location': {('location', 0): 2.5},
                                'Inv_cost_network': {0: 2.5},
                                'X_P': {('location', 'process_certain_capacity', 0): 1.0,
                                        ('location', 'process_deterministic_capacity', 0): 1.0,
                                        ('location', 'process_deterministic_capacity2', 0): -0.0,
                                        ('location', 'process_storage', 0): 1.0,
                                        ('location', 'process_storage_discharge', 0): 1.0},
                                'X_S': {('location',
                                         'process_storage_resource_deterministic_demand_stored',
                                         0): 1.0},
                                'objective': 47423.333})