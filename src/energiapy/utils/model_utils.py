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
import pandas
from ..components.temporal_scale import Temporal_scale
from ..components.resource import Resource


def create_dummy_resource(resource: Resource, store_max: float = 0, store_min: float = 0):
    
    resource_dummy = Resource(name = resource.name + '_stored', loss = resource.loss, store_max= store_max, \
        store_min = store_min, basis = resource.basis, block = resource.block + '(stored)', label = resource.label + '(stored)')
    
    return resource_dummy



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

def scale_changer(input_dict:dict, scales: Temporal_scale, scale_level: int)-> dict:
    """changes the scales form datetime to tuples 
    """
    df = pandas.concat([pandas.DataFrame(input_dict[list(input_dict.keys())[i]])\
    for i in range(len(input_dict.keys()))], axis = 1)   
    # df['hour'] = pandas.to_datetime(df.index, errors='coerce').strftime("%H")
    # df['day'] = pandas.to_datetime(df.index, errors='coerce').strftime("%j")
    # df['year'] = pandas.to_datetime(df.index, errors='coerce').strftime("%Y")
    # c = df['day']
    # if scales.start_zero is not None:
    #     df['scales'] = [(int(i)  - scales.start_zero, int(j) - 1, int(k)) \
    #         for i,j,k in zip(df['year'], df['day'], df['hour'])]
    # else:
    #     df['scales'] = [(0, int(j) - 1, int(k)) \
    #         for i,j,k in zip(df['year'], df['day'], df['hour'])]
    # df = df.drop(['hour', 'day', 'year'], axis = 1)
    df['scales'] = scales.scale_iter(scale_level = scale_level)
    df = df.set_index(['scales'])
    df.columns = [i.name for i in input_dict.keys()]
    df = df.apply(lambda x:x/x.max(), axis = 0)   
    output_dict = {i: {j: df[i][j] for j in df.index } for i in df.columns}

    return output_dict
