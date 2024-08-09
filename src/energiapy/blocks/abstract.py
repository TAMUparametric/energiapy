from dataclasses import dataclass, field

from .._core._handy._dunders import _Dunders


@dataclass
class Abstract(_Dunders):
    """Abstract Tasks for the model"""

    name: str = field(default=None)

    def __post_init__(self):
        self.name = f'Abstract|{self.name}|'
        self.tasks = []
