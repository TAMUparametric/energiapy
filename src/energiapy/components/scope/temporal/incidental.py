"""Used as a decorator for Incidental Parameters
"""

from dataclasses import dataclass, field

from pandas import DataFrame

from ....core._handy._dunders import _Dunders


@dataclass
class I(_Dunders):
    """Incidental Parameter
    This is useful when a Parameteris not dependent on the Parent Variable

    Incidental Capital Expenditure or Fixed Operational Expenditure are examples

    Attributes:
        value (IsIncidental): The incidental value
    """

    value: int | float | DataFrame = field(default=None)

    def __post_init__(self):
        self.name = 'i'
