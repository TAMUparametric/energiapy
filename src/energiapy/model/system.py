from dataclasses import dataclass, field

from .._core._handy._dunders import _Dunders
from .._core._handy._sets import _ComponentSets
from ..funcs.add_to.component import add_component


@dataclass
class System(_Dunders, _ComponentSets):
    """Collects System Components"""

    name: str = field(default=None)

    def __post_init__(self):
        _ComponentSets.__post_init__(self)

        self.name = f'System|{self.name}|'

        # there are only one each of these

        self.network, self.horizon = None, None


