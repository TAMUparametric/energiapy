"""Index is attached to parameters, variables, and constraints
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._core._aliases._is_component import (
        IsCash,
        IsEmission,
        IsLand,
        IsLinkage,
        IsLocation,
        IsMaterial,
        IsPlayer,
        IsProcess,
        IsResource,
        IsScale,
        IsStorage,
        IsTransit,
        IsNetwork,
    )


@dataclass
class Disposition:
    """The spatiotemporal disposition of the Component"""

    # Do not reorder these fields
    ply: IsPlayer = field(default=None)
    emn: IsEmission = field(default=None)
    csh: IsCash = field(default=None)
    res: IsResource = field(default=None)
    mat: IsMaterial = field(default=None)
    lnd: IsLand = field(default=None)
    pro: IsProcess = field(default=None)
    stg: IsStorage = field(default=None)
    trn: IsTransit = field(default=None)
    loc: IsLocation = field(default=None)
    lnk: IsLinkage = field(default=None)
    ntw: IsNetwork = field(default=None)
    scl: IsScale = field(default=None)

    def __post_init__(self):

        # this is the component index
        self.index = tuple(
            [getattr(self, i.name) for i in fields(self) if getattr(self, i.name)]
        )

        # this maintains the order of the components in the index
        self.name = f'{tuple(dict.fromkeys(self.index).keys())}'

    def args(self):
        """provides a dict of attributes"""
        return {i.name: getattr(self, i.name) for i in fields(self)}

    def idx(self):
        """Gives the full index list, by expanding the temporal index"""
        return [(*[k.name for k in self.index[:-1]], *j) for j in self.scl.index if j]

    def __len__(self):
        return len(self.scl)
