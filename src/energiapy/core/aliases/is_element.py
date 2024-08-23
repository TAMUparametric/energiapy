"""TypeAliases for Program Elements 
"""

from typing import TypeAlias, Union

from .is_constraint import IsConstraint
from .is_parameter import IsParameter
from .is_variable import IsVariable

IsElement: TypeAlias = Union[IsParameter, IsVariable, IsConstraint]
