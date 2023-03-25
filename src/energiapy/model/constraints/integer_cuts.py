"""pyomo integer cuts
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2023, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "0.0.1"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

# from pyomo.environ import ConcreteModel, Constraint
# from ...utils.latex_utils import constraint_latex_render
# from ...utils.scale_utils import scale_list
# from ...utils.scale_utils import scale_pyomo_set
# from ...utils.scale_utils import scale_tuple
# from ...components.location import Location
# from itertools import product
# from typing import Union
# from enum import Enum, auto



# def constraint_block_integer_cut(instance: ConcreteModel, network_scale_level: int, location: Location, block: 'str', number:int = 1) -> Constraint:
#     """Ensures atleast n components in block are set

#     Args:
#         instance (ConcreteModel): pyomo instance
#         block (str): block over which to apply constraint
#     Returns:
#         Constraint: block_integer_cut
#     """
#     scales = scale_list(instance=instance, scale_levels=network_scale_level+1)

#     def block_integer_cut_rule(instance, location, *scale_list):
#         return sum(instance.X_P[location, i, scale_list] for i in process_set) == number 
#     instance.constraint_block_integer_cut = Constraint(
#         instance.locations, *scales, rule=block_integer_cut_rule, doc='block integer cut')
#     constraint_latex_render(block_integer_cut_rule)
#     return instance.constraint_block_integer_cut

# TODO make integer cuts file separate from formulate