"""Planning Horizon of the problem
"""

from dataclasses import dataclass

from ...core._handy._dunders import _Dunders
from .scale import Scale


@dataclass
class Horizon(_Dunders):
    """Planning Horizon of the problem"""

    def __post_init__(self):
        self.scales: list[Scale] = []

    def __setattr__(self, name, scale):

        if isinstance(scale, Scale):
            self.scales.append(scale)

        super().__setattr__(name, scale)
