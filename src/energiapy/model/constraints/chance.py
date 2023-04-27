"""chance constraints
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2023, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "MIT"
__version__ = "1.0.5"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from typing import Union, Dict

from pyomo.environ import ConcreteModel, Constraint

from ...utils.latex_utils import constraint_latex_render
from ...utils.scale_utils import scale_list, scale_tuple
from ...fitting.dist import fit
from ...utils.data_utils import  min_max


# def constraint_demand_chance(instance: ConcreteModel, demand_factor:dict, guarantee: float, dist:str = 'norm', demand_scale_level: int = 0, scheduling_scale_level: int = 0,loc_res_dict: dict = None, ) -> Constraint:

#     # scales = scale_list(instance= instance, scale_levels = demand_scale_level+1)
#     scales = scale_list(instance=instance,
#                         scale_levels=len(instance.scales))
#     scale_iter = scale_tuple(
#         instance=instance, scale_levels=scheduling_scale_level + 1)

#     if loc_res_dict is None:
#         loc_res_dict = dict()
    
#     def norm_constant(p, mu, sigma):
#         x = mu + erf(1 / sqrt(2) * p) * sigma * sqrt(2)
#         return 1 / (sigma * sqrt(2 * pi)) * exp(-(x - mu)**2 / (2 * sigma**2))

#         data = demand_factor[location].to_numpy()
#         data = min_max(data)
#         fit_summary = fit(data)
#         mu = fit_summary.loc[dist]['loc']
#         sigma = fit_summary.loc[dist]['scale']
#         c= norm_constant(guarantee, mu, sigma)


#     def demand_chance_rule(instance, location, resource, *scale_list):
     
#     constraint_latex_render(demand_chance_rule)
#     return instance.constraint_demand
