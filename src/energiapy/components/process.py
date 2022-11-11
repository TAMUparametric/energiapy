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

from dataclasses import dataclass, field
from typing import Dict, Union
from ..components.resource import Resource
from ..components.material import Material
import pandas
from random import sample

@dataclass
class Process:
    """
    Object with process data
    Args:
        name (str): ID
        conversion (Dict[resource, float], optional): conversion data. Defaults to None.
        cost (floatordict, optional): cost of operation. Defaults to None.
        material_cons (Dict[material, float], optional): material consumption data. Defaults to None.
        varying (bool, optional): if production capacity is varying. Defaults to False.
        intro_scale (int, optional): scale when process is introduced. Defaults to 0.
        prod_max (float, optional): maximum production. Defaults to 0.
        prod_min (float, optional): minimum production. Defaults to 0.
        cap_seg (dict, optional): capacity pwl segment. Defaults to None.
        capex_seg (dict, optional): capex pwl segment. Defaults to None.
        carbon_credit (bool, optional): does process earn carbon credits. Defaults to False.
        basis(str, optional): base units for operation. Defaults to 'unit'.
        gwp (float, optional): global warming potential per basis. Defaults to 0.
        land (float, optional): land requirement. Defaults to 0.
        trl (str, optional): technology readiness level. Defaults to None.
        block (str, optional): define block for convenience. Defaults to None.
        citation (str, optional): citation for data. Defaults to 'citation needed'.
        lifetime (float, optional): the lifetime of process. Defaults to None.
        varying (bool, optional): whether process is subject to uncertainty. Defaults to False.
        varying_capacity_df (pandas.DataFrame, optional): input dataframe to generate capacity factors. Defaults to None.  
    """

    name: str 
    conversion: Dict[Resource, float] = field(default_factory= dict)
    cost: Union[float, dict] = None #field(default_factory = dict) 
    material_cons: Dict[Material, float] = field(default_factory= dict)
    label: str = ''
    intro_scale: int = 0
    prod_max: float = 0
    prod_min: float = 0.01
    cap_seg: dict = field(default_factory= dict)
    capex_seg: dict = field(default_factory= dict)
    basis: str = 'unit'
    carbon_credit: bool = False
    gwp: tuple = None
    land: float = 0
    trl: str = ''
    block: str = None
    citation: str = 'citation needed'
    lifetime: tuple = None
    varying:bool = False
    varying_capacity_df: pandas.DataFrame = None
    p_fail: float = None

    def __post_init__(self):
        if self.cost is not None:
            self.capex = self.cost['CAPEX']
            self.fopex = self.cost['Fixed O&M']
            self.vopex = self.cost['Variable O&M']            
        else:
            self.capex = 100
            self.fopex = 10
            self.vopex = 1
        self.capacity_factor = self.make_capacity_factor()

    def make_capacity_factor(self)-> dict:
        """makes capacity factor dict from varying process/production output DataFrame()

        Returns:
            dict: dictionary with varying capacity factor, structure - {process: scale: value}
        """
        if self.varying_capacity_df is None:
            return None
        else:
            self.varying = True
            df = pandas.DataFrame(self.varying_capacity_df)
            df['hour'] = pandas.to_datetime(df.index, errors='coerce').strftime("%H")
            df['day'] = pandas.to_datetime(df.index, errors='coerce').strftime("%j")
            df['scales'] = [(0,int(j) - 1, int(k)) for j,k in zip(df['day'], df['hour'])]
            df = df.drop(['hour', 'day'], axis = 1)
            df.columns = ['value', 'scales']
            capacity_factor = {scale_: df['value'][df['scales'] == scale_][0]/max(df['value']) for scale_ in df['scales']}
            return capacity_factor
        
         
    def __repr__(self):
        return self.name
    
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
