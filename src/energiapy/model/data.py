from dataclasses import dataclass, field

from .._core._handy._dunders import _Dunders


@dataclass
class Data(_Dunders):
    """Is the data required for the model"""

    name: str = field(default=None)

    def __post_init__(self):
        self.name = f'Data|{self.name}|'
        self.constants, self.ms, self.thetas, self.datasets = ([] for _ in range(4))
