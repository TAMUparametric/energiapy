from dataclasses import dataclass, field

from .._core._handy._dunders import _Dunders


@dataclass
class Matrix(_Dunders):
    """Matrix representation of the Model"""

    name: str = field(default=None)

    def __post_init__(self):
        self.name = f'Matrix|{self.name}|'
