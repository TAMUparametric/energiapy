"""Type aliases for Constraints"""

from typing import TypeAlias, Union

from ...constraints.bind import Bind
from ...constraints.calculate import Calculate

IsBind: TypeAlias = Bind
IsCalculate: TypeAlias = Calculate

IsConstraint: TypeAlias = Union[IsBind, IsCalculate]
