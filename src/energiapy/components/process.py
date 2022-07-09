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

    def __init__(self, name: str, conversion: dict, label: str = '', year: int = 0, prod_max: float = 0, prod_min: float = 0, cap_seg: dict = {}, capex_seg: dict = {},
                 carbon_credit: bool = False, gwp: float = 0, land: float = 0, trl: str = '', block: str = '', source: str = 'citation needed'):
        """process object parameters

        Args:
            name (str): ID for process
            conversion (dict): conversion data
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
    
# %%
