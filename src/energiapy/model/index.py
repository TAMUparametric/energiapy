"""Index is attached to parameters, variables, and constraints   
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..funcs.general import Dunders, Magics

if TYPE_CHECKING:
    from .type.alias import IsAspect, IsComponent, IsDeclaredAt, IsTemporal


@dataclass
class Index(Dunders, Magics):
    component: IsComponent
    declared_at: IsDeclaredAt
    temporal: IsTemporal

    def __post_init__(self):

        comp = f'{self.component.name}'
        temp = f'{self.temporal.name.lower()}'

        if isinstance(self.declared_at, tuple):
            dec_at = f'{self.declared_at[0].name, self.declared_at[1].name}'
            index_list = [comp, dec_at, temp]
        elif self.component == self.declared_at:
            dec_at = ''
            index_list = [comp, temp]
        else:
            dec_at = f'{self.declared_at.name}'
            index_list = [comp, dec_at, temp]

        self.name = f'{tuple(dict.fromkeys(index_list).keys())}'
        self.index_list = index_list

    def full(self):
        """Gives the full index list, by expanding the temporal index
        """
        return [(*self.index_list[:-1], *j) for j in self.temporal.index]

    def __len__(self):
        return self.temporal.n_index
