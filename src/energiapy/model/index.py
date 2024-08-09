"""Index is attached to parameters, variables, and constraints   
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import TYPE_CHECKING

from ..core.inits.common import ElmCommon

if TYPE_CHECKING:
    from ..types import IsCommodity, IsOperation, IsScale, IsSpatial


@dataclass
class Index(ElmCommon):
    _derived: IsCommodity = field(default=None)
    _commodity: IsCommodity = field(default=None)
    _operation: IsOperation = field(default=None)
    _spatial: IsSpatial = field(default=None)
    _scale: IsScale = field(default=None)

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
