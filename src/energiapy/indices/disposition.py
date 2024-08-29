"""Index is attached to parameters, variables, and constraints
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import TYPE_CHECKING

from sympy import Idx, symbols

from ..core._handy._dunders import _Dunders

if TYPE_CHECKING:
    from ..core.aliases.is_component import (IsCash, IsComponent, IsEmission,
                                             IsLand, IsLinkage, IsLocation,
                                             IsMaterial, IsNetwork, IsPlayer,
                                             IsProcess, IsResource, IsScale,
                                             IsStorage, IsTransit)
    from ..core.aliases.is_value import IsMode


@dataclass
class Disposition(_Dunders):
    """The spatiotemporal disposition of the Component
    Disposition is the index of the a Program Model Element
    Gives you an idea of where the Parameter, Variable, or Constraint exists

    Attributes:
        ply (IsPlayer): Player
        emn (IsEmission): Emission
        csh (IsCash): Cash
        res (IsResource): Resource
        mat (IsMaterial): Material
        lnd (IsLand): Land
        pro (IsProcess): Process
        stg (IsStorage): Storage
        trn (IsTransit): Transit
        loc (IsLocation): Location
        lnk (IsLinkage): Linkage
        ntw (IsNetwork): Network
        scl (IsScale): Scale
        mde (IsMode): Mode



    """

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
    mde: IsMode = field(default=None)

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

    def structure(self):
        """provides the structure of the disposition"""
        return [i.name for i in fields(self) if getattr(self, i.name)]

    def childless(self, child: IsComponent):
        """Gives the disposition with the component removed"""
        return {
            i.name: getattr(self, i.name)
            for i in fields(self)
            if not isinstance(getattr(self, i.name), child)
        }

    def scaledown(self):
        """Goes to a lower scale"""
        return Disposition(**self.args())

    def __len__(self):
        return len(self.scl)

    @property
    def sym(self):
        """Symbol"""
        return symbols(",".join([f'{i}' for i in self.index]), cls=Idx)
