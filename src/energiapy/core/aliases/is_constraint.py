"""Type aliases for Constraints"""

from typing import TypeAlias, Union

from ...constraints.bind import Bind
from ...constraints.calculate import Calculate
from ...constraints.sumover import SumOver

IsBind: TypeAlias = Bind
IsCalculate: TypeAlias = Calculate
IsSumOver: TypeAlias = SumOver

IsConstraint: TypeAlias = Union[IsBind, IsCalculate, IsSumOver]
