"""Index is attached to parameters, variables, and constraints   
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._core._aliases._is_component import     IsAnalytical, IsAsset, IsCommodity, IsImpact, IsOperational, IsScope, IsSpatial, IsTemporal,


@dataclass
class Index:
    analytical: 
    asset: IsCommodity = field(default=None)
    commodity: IsCommodity = field(default=None)
    operational: IsOperational = field(default=None)
    spatial: IsSpatial = field(default=None)
    scale: IsScale = field(default=None)

    def __post_init__(self):

        self.index = tuple(
            [getattr(self, i.name) for i in fields(self) if getattr(self, i.name)]
        )

        self.name = f'{tuple(dict.fromkeys(self.index).keys())}'

    @property
    def args(self):
        """provides a dict of attributes"""
        return {i.name: getattr(self, i.name) for i in fields(self)}

    def full(self):
        """Gives the full index list, by expanding the temporal index"""
        return [
            (*[k.name for k in self.index[:-1]], *j) for j in self._scale.index if j
        ]

    def __len__(self):
        return self._scale.n_index
