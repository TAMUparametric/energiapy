"""Index is attached to parameters, variables, and constraints   
"""
from __future__ import annotations

from dataclasses import dataclass, field
from operator import is_not
from typing import TYPE_CHECKING

from ..core.inits.common import ElmCommon

if TYPE_CHECKING:
    from ..types.alias import (IsCommodity, IsOperation, IsPlayer, IsScale,
                               IsSpatial)


@dataclass
class Index(ElmCommon):
    player: IsPlayer = field(default=None)
    derived: IsCommodity = field(default=None)
    commodity: IsCommodity = field(default=None)
    operation: IsOperation = field(default=None)
    spatial: IsSpatial = field(default=None)
    scale: IsScale = field(default=None)

    def __post_init__(self):

        ply_, der_, cmd_, opn_ = (f'{getattr(self,i).name}' if i else '' for i in [
            'player', 'derived', 'commodity', 'operation'])

        scl_ = f'{self.scale.name.lower()}'

        index_list = [i for i in [der_, cmd_, opn_, scl_] if is_not(i, '')]

        self.name = f'[{ply_}]{tuple(dict.fromkeys(index_list).keys())}'
        self.index_list = index_list

    def full(self):
        """Gives the full index list, by expanding the temporal index
        """
        return [(*self.index_list[:-1], *j) for j in self.scale.index]

    def __len__(self):
        return self.scale.n_index
