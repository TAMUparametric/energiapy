"""TypeAliases for Program Elements 
"""

from typing import TypeAlias, Union

from .iscns import IsConstraint
from .isprm import IsParameter
from .isvar import IsVariable

IsElement: TypeAlias = Union[IsParameter, IsVariable, IsConstraint]
