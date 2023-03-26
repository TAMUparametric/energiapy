# %%
"""Generates latex doc string
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "MIT"
__version__ = "1.0.5"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

import inspect


def constraint_latex_render(constraint_rule, latex_alias_dict: dict = None) -> str:
    """renders a string for equation in latex format

    Args:
        constraint_rule (function, optional): constraint definition rule. Defaults to {}
        latex_alias_dict (dict): aliases for vaiables, sets, and symbols

    Returns:
        str: string in latex format
    """

    if latex_alias_dict is None:
        latex_alias_dict = dict()

    general_dict = {
        'product': '\prod',
        'sum': '\sum',
        '**': '^',
        '*': '.',
        '==': '=',
        '<=': '\leq',
        '>=': '\geq',
        '[': '(',
        ']': ')',
        'exp': 'exp',
        'instance.': '',
        'location': 'l',
        'resource': 'r',
        'network': 'n',
        'scale_list[:scheduling_scale_level+1]': 'y,d,h',
        'scale_list[:network_scale_level+1]': 'y',
        'scale_list[:expenditure_scale_level+1]': 'y,d',
        '[location][resource]': '(l,r)',
        'cons_max': 'C^{max}',
        'price': 'R^{base}',
        'process': 'p',
        'P_location': 'P^{l}',
        'C_location': 'C^{l}',
        'S_location': 'S^{l}',
        'B_location': 'B^{l}',
        'P_network': 'P^{n}',
        'C_network': 'C^{n}',
        'S_network': 'S^{n}',
        'B_network': 'B^{n}',
        'annualization_factor': 'A^{f}',
        'scale_list': 'y',
        'for location_ in instance.locations': '',
        'for process_ in instance.processes': '',
        'for resource_ in instance.resources': '',
        'capex_dict': 'Capex^{unit}',
        'fopex_dict': 'Opex^{unit, fix}',
        'vopex_dict': 'Opex^{unit, var}',
        'Cap_P': 'Cap^{P}',
        'Cap_S': 'Cap^{S}',
        'instance.Fopex': 'Opex^{fix}',
        'instance.Vopex': 'Opex^{var}',
        'demand_dict': 'Demand^{r}',
        'for scale_ in scale_iter if scale_[:demand_scale_level+1] == scale_list': '',
        'for transport_ in instance.transports': '',
        '_exp': '^{exp}',
        '_imp': '^{imp}',
        'source': 'l^{source}',
        'sink': 'l^{sink}',
        'transport_': 't',
        'transport': 't',
    }

    unsorted_dict_ = {**latex_alias_dict, **general_dict}

    list_ = list(unsorted_dict_.keys())
    list_.sort(key=len)
    list_.reverse()

    dict_ = {i: unsorted_dict_[i] for i in list_}
    str_ = inspect.getsource(constraint_rule).split(
        'return ')[1].split('\n')[0]
    for key in dict_.keys():
        str_ = str_.replace(key, dict_[key])

    # str_ = '\begin{equation}'

    print_ = str(constraint_rule)
    print_ = print_.split('<function ')[1]
    try:
        print_ = print_.split('.<locals>')[0]
    except:
        print_ = print_.split('at')[0]
    finally:
        print_ = print_
    print_ = print_.replace('_', ' ')
    print(print_)

    return str_


# %%
