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
