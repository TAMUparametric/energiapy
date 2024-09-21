"""Index gives the disposition of Program Elements (Variables, Parameters, Constraints)
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import TYPE_CHECKING

from sympy import Idx, symbols

from ..core._handy._dunders import _Dunders

if TYPE_CHECKING:
    from ..components._base._component import _Component
    from ..components.analytical.player import Player
    from ..components.commodity.cash import Cash
    from ..components.commodity.emission import Emission
    from ..components.commodity.land import Land
    from ..components.commodity.resource import Resource
    from ..components.process import Process
    from ..components.operation.storage import Storage
    from ..components.operation.transit import Transit
    from ..components.spatial.linkage import Linkage
    from ..components.spatial.location import Location
    from ..components.temporal.mode import X
    from ..components.temporal.scale import Scale


@dataclass
class Index(_Dunders):
    """The spatiotemporal disposition of the Component
    Index is the index of the a Program Model Element
    Gives you an idea of where the Parameter, Variable, or Constraint exists

    Attributes:
        ply (Player): Player
        emn (Emission): Emission
        csh (Cash): Cash
        res (Resource): Resource
        lnd (Land): Land
        pro (Process): Process
        stg (Storage): Storage
        trn (Transit): Transit
        loc (Location): Location
        lnk (Linkage): Linkage
        ntw (Network): Network
        scl (Scale): Scale
        mde (Mode): Mode
    """

    # Do not reorder these fields, Please
    ply: Player = field(default=None)
    emn: Emission = field(default=None)
    csh: Cash = field(default=None)
    res: Resource = field(default=None)
    lnd: Land = field(default=None)
    pro: Process = field(default=None)
    stg: Storage = field(default=None)
    trn: Transit = field(default=None)
    loc: Location = field(default=None)
    lnk: Linkage = field(default=None)
    scl: Scale = field(default=None)
    mde: X = field(default=None)

    def __post_init__(self):
        
        # this is the disposition of the Program Element
        self.disposition = tuple(
            [getattr(self, f.name) for f in fields(self) if getattr(self, f.name)]
        )

        # this maintains the order of the components in the disposition
        self.name = f'{tuple(dict.fromkeys(self.disposition).keys())}'

    def args(self):
        """provides a dict of attributes"""
        return {f.name: getattr(self, f.name) for f in fields(self)}

    def childless(self, child: _Component):
        """Gives a disposition without the component"""
        return {k: cmp for k, cmp in self.args().items() if cmp != child}

    def __len__(self):
        return len(self.scl)

    def size(self):
        """Size of the Index"""
        return len(self.disposition)

    @property
    def sym(self):
        """Symbol"""
        return symbols(",".join([f'{d}' for d in self.disposition]), cls=Idx)
