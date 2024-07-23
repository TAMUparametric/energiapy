from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .type.aliases import IsAspect, IsComponent, IsTemporal, IsDeclaredAt


@dataclass
class Index:
    component: IsComponent
    declared_at: IsDeclaredAt
    temporal: IsTemporal

    def __post_init__(self):

        if isinstance(self.declared_at, tuple):
            dec_at = f'{self.declared_at[0].name, self.declared_at[1].name}'

        elif self.component == self.declared_at:
            dec_at = ''

        else:
            dec_at = f'{self.declared_at.name}'

        comp = f'{self.component.name}'
        temp = f'{self.temporal.name.lower()}'

        self.name = f'{tuple(dict.fromkeys([comp, dec_at, temp]).keys())}'

    def __len__(self):
        return self.temporal.n_index

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
