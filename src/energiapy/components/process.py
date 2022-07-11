#%%
"""Process data class  
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

@dataclass
class process:
    """
    Object with process data
    """

    def __init__(self, name: str, conversion: dict= None, cost:float or dict = None, material_cons:float or dict = None, label: str = None, year: int = 0, prod_max: float = 0, prod_min: float = 0, cap_seg: dict = None, capex_seg: dict = None,
                 carbon_credit: bool = False, gwp: float = 0, land: float = 0, trl: str = None, block: str = None, source: str = 'citation needed'):
        """process object parameters
        Args:
            name (str): ID for process
            conversion (dict, optional): conversion data
            cost(float, optional): process costs
            material(float, optional): materials required
            label (str, optional): name of the process. Defaults to ''.
            year (int, optional): Year when process is introduced. Defaults to 0.
            prod_max (float, optional): Maximum allowed capacity increase in a year. Defaults to 0.
            prod_min (float, optional): Minimum allowed capacity increase in a year. Defaults to 0.
            cap_seg (float, optional): capacity segment for pwl costing. Defaults to {}.
            capex_seg (float, optional): capex segment for pwl costing. Defaults to {}.
            carbon_credit(bool, optional): True if carbon tax credits are earned through the process. Defaults to False
            gwp (float, optional): global warming potential for process. Defaults to 0.
            land (float, optional): land use per production of nominal resource. Defaults to 0.
            trl (str, optional): TRL level of the process. Defaults to ''.
            block (str, optional): representative block. Defaults to ''.
            source (str, optional): data source. Defaults to ''.

        """
        self.name = name
        # self.conversion = {resource.name: conversion[resource] for resource in conversion.keys()}
        self.conversion = conversion
        self.cost = cost 
        self.material_cons = material_cons
        self.label = label
        self.year = year
        self.prod_max = prod_max
        self.prod_min = prod_min
        self.cap_seg = cap_seg
        self.capex_seg = capex_seg
        self.carbon_credit = carbon_credit
        self.gwp = gwp
        self.land = land
        self.trl = trl
        self.block = block
        self.source = source

    def __repr__(self):
        return self.name

    # class cost_scenario:
    #     """
    #     Onject with data regarding a cost scenario
    #     """

    #     def __init__(self, name: str, horizon: float, label: str = '', enterprise: float = '', utility: float = '', pilot: float = '', repurposed: float = ''):
    #         """cost scenario parameters

    #         Args:
    #             name (str): ID for the cost scenario
    #             label (str, optional): name of the location. Defaults to ''.
    #             horizon (float): length of planning horizon
    #             enterprise (float, optional): reduction in cost over horizon for enterprise TRL. Defaults to ''.
    #             utility (float, optional): reduction in cost over horizon for utility TRL. Defaults to ''.
    #             pilot (float, optional): reduction in cost over horizon for pilot TRL. Defaults to ''.
    #             repurposed (float, optional): reduction in cost over horizon for repurposed TRL. Defaults to ''.
    #         """
    #         self.name = name
    #         self.label = label
    #         self.horizon = horizon
    #         self.enterprise = enterprise
    #         self.utility = utility
    #         self.pilot = pilot
    #         self.repurposed = repurposed

    #     def __repr__(self):
    #         return self.name

    # def fill_cost(cost_dict: dict, process, location_list: list, cost_scenario_list: list,
    #             year_list: list, cost_parameters: dict, nrel_cost_dict:dict = {}): #: pandas.DataFrame = {}):
    #     """fills cost_dict with costing data(CAPEX, Variable and Fixed OPEX), nominal basis (units), and source
    #     data can be user-defined or taken from NREL

    #     Args:
    #         cost_dict (dict): contains cost data for processes
    #         process ([type]): process object
    #         location_list (list): set of locations
    #         cost_scenario_list (list): set of scenarios
    #         cost_parameters (dict): feeds values for cost metrics
    #         nrel_cost_df (pandas.DataFrame): contains data from NREL ATB
    #     """
    #     cost_metrics_list = ['CAPEX', 'Fixed O&M',
    #                         'Variable O&M', 'units', 'source']

    #     for location, cost_scenario, year, cost_metric in product(location_list, cost_scenario_list, year_list, cost_metrics_list):
    #         if cost_metric == 'source':
    #             cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_parameters['source']

    #         elif cost_metric in ['CAPEX', 'Fixed O&M', 'Variable O&M']:
    #             if process.trl == 'enterprise':
    #                 if year == 0:
    #                     cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_parameters[cost_metric]
    #                 elif year > 0 and year <= 10:
    #                     cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_dict[location.name][
    #                         cost_scenario.name][process.name][year-1][cost_metric]*(1 - 1.05*cost_scenario.enterprise*year)
    #                 elif year > 10 and year <= 20:
    #                     cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_dict[location.name][
    #                         cost_scenario.name][process.name][year-1][cost_metric]*(1 - 1.05*cost_scenario.enterprise*year)
    #                 else:
    #                     cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_dict[location.name][
    #                         cost_scenario.name][process.name][year-1][cost_metric]*(1 - 0.04*cost_scenario.enterprise*year)

    #             elif process.trl == 'utility':
    #                 if year == 0:
    #                     cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_parameters[cost_metric]
    #                 elif year > 0 and year <= 10:
    #                     cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_dict[location.name][
    #                         cost_scenario.name][process.name][year-1][cost_metric]*(1 - 1.6*cost_scenario.utility*year)
    #                 elif year > 10 and year <= 20:
    #                     cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_dict[location.name][
    #                         cost_scenario.name][process.name][year-1][cost_metric]*(1 - 1.2*cost_scenario.utility*year)
    #                 else:
    #                     cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_dict[location.name][
    #                         cost_scenario.name][process.name][year-1][cost_metric]*(1 - 1.0*cost_scenario.utility*year)

    #             elif process.trl == 'pilot':
    #                 if year == 0:
    #                     cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_parameters[cost_metric]
    #                 elif year > 0 and year <= 10:
    #                     cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_dict[
    #                         location.name][cost_scenario.name][process.name][year-1][cost_metric]*(1 - cost_scenario.pilot*year)
    #                 elif year > 10 and year <= 20:
    #                     cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_dict[location.name][
    #                         cost_scenario.name][process.name][year-1][cost_metric]*(1 - 1.6*cost_scenario.pilot*year)
    #                 else:
    #                     cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_dict[location.name][
    #                         cost_scenario.name][process.name][year-1][cost_metric]*(1 - 1.1*cost_scenario.pilot*year)

    #             elif process.trl == 'repurposed':
    #                 cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_parameters[cost_metric]*(
    #                     1 - cost_scenario.repurposed*year/(cost_scenario.horizon-1))
    #             elif process.trl == 'discharge':
    #                 cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_parameters[cost_metric]
    #             elif process.trl == 'nocost':
    #                 cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = 0
    #             elif process.trl == 'nrel':
    #                 dict_ = nrel_cost_dict
    #                 value = dict_[location.name]['cost'][((dict_[location.name]['metric'] == cost_metric) & (dict_[location.name]['process'] == process.name) & (
    #                     dict_[location.name]['cost_scenario_list'] == cost_scenario.name) & (dict_[location.name]['year'] == year))].values
    #                 if not value.any():
    #                     cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = 0
    #                 else:
    #                     cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = value[0]

    #         elif cost_metric == 'units':
    #             if process.trl == 'nrel':
    #                 dict_ = nrel_cost_dict
    #                 cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] \
    #                     = dict_[location.name]['units'][((dict_[location.name]['metric'].isin(cost_metrics_list)) & (dict_[location.name]['process'] == process.name) & (dict_[location.name]['cost_scenario_list'] == cost_scenario.name) & (dict_[location.name]['year'] == year))].values[0]
    #             elif process.trl == 'nocost':
    #                 cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = 'None'
    #             else:
    #                 cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] \
    #                     = cost_parameters['units']

    #     return

    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        return self.name == other.name
        

    # class cost_scenario:
    #     """
    #     Onject with data regarding a cost scenario
    #     """

    #     def __init__(self, name: str, horizon: float, label: str = '', enterprise: float = '', utility: float = '', pilot: float = '', repurposed: float = ''):
    #         """cost scenario parameters

    #         Args:
    #             name (str): ID for the cost scenario
    #             label (str, optional): name of the location. Defaults to ''.
    #             horizon (float): length of planning horizon
    #             enterprise (float, optional): reduction in cost over horizon for enterprise TRL. Defaults to ''.
    #             utility (float, optional): reduction in cost over horizon for utility TRL. Defaults to ''.
    #             pilot (float, optional): reduction in cost over horizon for pilot TRL. Defaults to ''.
    #             repurposed (float, optional): reduction in cost over horizon for repurposed TRL. Defaults to ''.
    #         """
    #         self.name = name
    #         self.label = label
    #         self.horizon = horizon
    #         self.enterprise = enterprise
    #         self.utility = utility
    #         self.pilot = pilot
    #         self.repurposed = repurposed

    #     def __repr__(self):
    #         return self.name

    # def fill_cost(cost_dict: dict, process, location_list: list, cost_scenario_list: list,
    #             year_list: list, cost_parameters: dict, nrel_cost_dict:dict = {}): #: pandas.DataFrame = {}):
    #     """fills cost_dict with costing data(CAPEX, Variable and Fixed OPEX), nominal basis (units), and source
    #     data can be user-defined or taken from NREL

    #     Args:
    #         cost_dict (dict): contains cost data for processes
    #         process ([type]): process object
    #         location_list (list): set of locations
    #         cost_scenario_list (list): set of scenarios
    #         cost_parameters (dict): feeds values for cost metrics
    #         nrel_cost_df (pandas.DataFrame): contains data from NREL ATB
    #     """
    #     cost_metrics_list = ['CAPEX', 'Fixed O&M',
    #                         'Variable O&M', 'units', 'source']

    #     for location, cost_scenario, year, cost_metric in product(location_list, cost_scenario_list, year_list, cost_metrics_list):
    #         if cost_metric == 'source':
    #             cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_parameters['source']

    #         elif cost_metric in ['CAPEX', 'Fixed O&M', 'Variable O&M']:
    #             if process.trl == 'enterprise':
    #                 if year == 0:
    #                     cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_parameters[cost_metric]
    #                 elif year > 0 and year <= 10:
    #                     cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_dict[location.name][
    #                         cost_scenario.name][process.name][year-1][cost_metric]*(1 - 1.05*cost_scenario.enterprise*year)
    #                 elif year > 10 and year <= 20:
    #                     cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_dict[location.name][
    #                         cost_scenario.name][process.name][year-1][cost_metric]*(1 - 1.05*cost_scenario.enterprise*year)
    #                 else:
    #                     cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_dict[location.name][
    #                         cost_scenario.name][process.name][year-1][cost_metric]*(1 - 0.04*cost_scenario.enterprise*year)

    #             elif process.trl == 'utility':
    #                 if year == 0:
    #                     cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_parameters[cost_metric]
    #                 elif year > 0 and year <= 10:
    #                     cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_dict[location.name][
    #                         cost_scenario.name][process.name][year-1][cost_metric]*(1 - 1.6*cost_scenario.utility*year)
    #                 elif year > 10 and year <= 20:
    #                     cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_dict[location.name][
    #                         cost_scenario.name][process.name][year-1][cost_metric]*(1 - 1.2*cost_scenario.utility*year)
    #                 else:
    #                     cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_dict[location.name][
    #                         cost_scenario.name][process.name][year-1][cost_metric]*(1 - 1.0*cost_scenario.utility*year)

    #             elif process.trl == 'pilot':
    #                 if year == 0:
    #                     cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_parameters[cost_metric]
    #                 elif year > 0 and year <= 10:
    #                     cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_dict[
    #                         location.name][cost_scenario.name][process.name][year-1][cost_metric]*(1 - cost_scenario.pilot*year)
    #                 elif year > 10 and year <= 20:
    #                     cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_dict[location.name][
    #                         cost_scenario.name][process.name][year-1][cost_metric]*(1 - 1.6*cost_scenario.pilot*year)
    #                 else:
    #                     cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_dict[location.name][
    #                         cost_scenario.name][process.name][year-1][cost_metric]*(1 - 1.1*cost_scenario.pilot*year)

    #             elif process.trl == 'repurposed':
    #                 cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_parameters[cost_metric]*(
    #                     1 - cost_scenario.repurposed*year/(cost_scenario.horizon-1))
    #             elif process.trl == 'discharge':
    #                 cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = cost_parameters[cost_metric]
    #             elif process.trl == 'nocost':
    #                 cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = 0
    #             elif process.trl == 'nrel':
    #                 dict_ = nrel_cost_dict
    #                 value = dict_[location.name]['cost'][((dict_[location.name]['metric'] == cost_metric) & (dict_[location.name]['process'] == process.name) & (
    #                     dict_[location.name]['cost_scenario_list'] == cost_scenario.name) & (dict_[location.name]['year'] == year))].values
    #                 if not value.any():
    #                     cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = 0
    #                 else:
    #                     cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = value[0]

    #         elif cost_metric == 'units':
    #             if process.trl == 'nrel':
    #                 dict_ = nrel_cost_dict
    #                 cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] \
    #                     = dict_[location.name]['units'][((dict_[location.name]['metric'].isin(cost_metrics_list)) & (dict_[location.name]['process'] == process.name) & (dict_[location.name]['cost_scenario_list'] == cost_scenario.name) & (dict_[location.name]['year'] == year))].values[0]
    #             elif process.trl == 'nocost':
    #                 cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] = 'None'
    #             else:
    #                 cost_dict[location.name][cost_scenario.name][process.name][year][cost_metric] \
    #                     = cost_parameters['units']

    #     return

    
# %%
