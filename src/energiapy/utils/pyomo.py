import math
from itertools import product

import pandas
from pyomo.environ import ConcreteModel, Set

from ..components import Scale


def scale_pyomo_set(instance: ConcreteModel, scale_level: int = 0, doc: str = None):
    """returns a set with appropropriate scale(s)

    Args:
        instance (ConcreteModel): pyomo instance
        scale_level (int, optional): appropriate scale. Defaults to 0.
        doc (str, optional): name of set
    """
    list_ = [instance.scales[i].data() for i in range(scale_level + 1)]
    return Set(initialize=list(product(*list_)), doc=doc)


def scale_list(instance: ConcreteModel, scale_levels: int = 0):
    """returns a list with appropropriate scale(s)

    Args:
        instance (ConcreteModel): pyomo instance
        scale_level (int, optional): appropriate scale. Defaults to 0.
    """
    return [instance.scales[i].data() for i in range(scale_levels)]


def scale_tuple(instance: ConcreteModel, scale_levels: int = 0):
    """returns a tuple with appropropriate scale(s)

    Args:
        instance (ConcreteModel): pyomo instance
        scale_level (int, optional): appropriate scale. Defaults to 0.
    """
    data = [instance.scales[i].data() for i in range(scale_levels)]
    list_ = list(product(*data))
    return list_


def scale_changer(input_dict: dict, scales: Scale, scale_level: int) -> dict:
    """changes the scales form datetime to tuples"""
    df = pandas.concat(
        [
            pandas.DataFrame(input_dict[list(input_dict.keys())[i]]).reset_index(
                drop=True
            )
            for i in range(len(input_dict.keys()))
        ],
        axis=1,
    )
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
    df['scales'] = scales.scale_iter(scale_level=scale_level)
    df = df.set_index(['scales'])
    df.columns = [i.name for i in input_dict.keys()]
    df = df.apply(lambda x: x / x.max(), axis=0)
    output_dict = {
        i: {j: df[i][j] if math.isnan(df[i][j]) is False else 0.0 for j in df.index}
        for i in df.columns
    }

    return output_dict
