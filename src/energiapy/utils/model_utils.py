"""Model utilities  
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "0.0.1"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from itertools import product
from pyomo.environ import ConcreteModel, Set

def fetch_components(process_list: list, master_list: list, dict_with_relevant_data: dict) -> str:
    """Fetches a list of materials for which relevant data is available 
    conversion for example will be used draw resources from the specified processes

    Args:
        process_list (list): list of processes
        master_list (list): master list of all defined elements 
        dict_with_relevant_data (dict): dictionary to look up for matches, conversion with resources for example


    Returns:
        str: list of components
    """
    list_ = []
    for process, value in product(process_list, master_list):
        if dict_with_relevant_data[process.name][value.name] != 0:
            list_.append(value) if value not in list_ else list_
    return list_

def scale_pyomo_set(instance: ConcreteModel, scale_level:int=0):
    """returns a set with appropropriate scale(s)

    Args:
        instance (ConcreteModel): pyomo instance
        scale_level (int, optional): appropriate scale. Defaults to 0.
    """
    list_ = [instance.scales[i].data() for i in range(scale_level+ 1)]
    return  Set(initialize = [i for i in product(*list_)])


def scale_list(instance: ConcreteModel, scale_levels:int=0):
    """returns a list with appropropriate scale(s)

    Args:
        instance (ConcreteModel): pyomo instance
        scale_level (int, optional): appropriate scale. Defaults to 0.
    """
    return  [instance.scales[i].data() for i in range(scale_levels)]

def scale_tuple(instance: ConcreteModel, scale_levels:int=0):
    """returns a tuple with appropropriate scale(s)

    Args:
        instance (ConcreteModel): pyomo instance
        scale_level (int, optional): appropriate scale. Defaults to 0.
    """
    data = [instance.scales[i].data() for i in range(scale_levels)]
    list_ = [i for i in product(*data)]
    return  list_
