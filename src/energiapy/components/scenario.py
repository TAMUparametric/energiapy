"""Cost scenario data class  
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
class scenario:

    def __init__(self, name: str, process_list: list, conversion_dict:dict= {}, material_dict: {}):

    resource_list = fetch_components(process_list=process_list, master_list=all_resource_list, dict_with_relevant_data=conversion_dict) 
    def __repr__(self):
        return self.name

resource_list = fetch_components(
    process_list=process_list, master_list=all_resource_list, dict_with_relevant_data=conversion_dict)
material_list = fetch_components(
    process_list=process_list, master_list=all_material_list, dict_with_relevant_data=material_dict #put material requirements in the process class)
