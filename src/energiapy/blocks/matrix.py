"""Matrix representation of the Program Model
"""

from dataclasses import dataclass, field

from ..core._handy._dunders import _Dunders


@dataclass
class Matrix(_Dunders):
    """Matrix representation of the Program Model

    Attributes:
        name (str): Name, takes from Scenario

    """

    name: str = field(default=None)

    def __post_init__(self):
        self.name = f'Matrix|{self.name}|'
