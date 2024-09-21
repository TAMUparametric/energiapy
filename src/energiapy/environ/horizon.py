"""Planning Horizon of the problem
"""

from dataclasses import dataclass, field

from ..core._handy._dunders import _Dunders
from ..components.temporal.scale import Scale


@dataclass
class Horizon(_Dunders):
    """Planning Horizon of the problem"""

    name: str = field(default=None)

    def __post_init__(self):
        self.name = f'Horizon|{self.name}|'
        self.scales: list[Scale] = []

    def __setattr__(self, name, scale):

        if isinstance(scale, Scale):
            self.scales.append(scale)

        super().__setattr__(name, scale)
