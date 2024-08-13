"""TypeAliases for Program Elements 
"""

from typing import TypeAlias, Union

from ._is_parameter import IsParameter
from ._is_variable import IsVariable

IsElement: TypeAlias = Union[IsParameter, IsVariable]
