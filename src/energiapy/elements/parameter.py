from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING


from ..core.inits.common import ElmCommon
if TYPE_CHECKING:
    from ..components.horizon import Horizon
    from ..type.alias import IsValue


@dataclass
class Parameter(ElmCommon):
    value: IsValue

    def __post_init__(self):

        bnds = ['_varbound', '_spclimit', '_certainty', '_approach']
        disp = ['player', 'derived', 'commodity', 'operation', 'spatial']

        for i in bnds + disp + ['index']:
            setattr(self, i, getattr(self.value.index, i))

        if not hasattr(self, 'name'):
            self.name = f'{self.aspect.pname()}{self.bound.namer()}{self.index.name}'
