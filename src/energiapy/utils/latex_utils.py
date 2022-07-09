#%%
"""Generates latex doc string
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "0.0.1"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

import IPython.display as ip
import inspect

def constraint_latex_render(constraint_rule, latex_alias_dict:dict= {}) -> str:
    """renders a string for equation in latex format

    Args:
        constraint_rule (function, optional): constraint definition rule. Defaults to {}
        latex_alias_dict (dict): aliases for vaiables, sets, and symbols

    Returns:
        str: string in latex format
    """
    general_dict = {
        '**': '^',
        '*': '.',
        '==': '=',
        '<=': '\leq',
        '>=': '\geq',
        '[': '(',
        ']': ')',
        'exp': 'exp',
        'instance.':'',
        }
    
    unsorted_dict_ = {**latex_alias_dict, **general_dict}
    
    
    list_ = [i for i in unsorted_dict_.keys()]
    list_.sort(key = len)
    list_.reverse()

    dict_ = {i: unsorted_dict_[i] for i in list_}
    str_ = inspect.getsource(constraint_rule).split('return ')[1].split('\n')[0]
    for key in dict_.keys():
        str_ = str_.replace(key, dict_[key])
    # str_ = '\begin{equation}'
    ip.display(ip.Math(str_))
    # display(str_)
    
    return str_

# %%
