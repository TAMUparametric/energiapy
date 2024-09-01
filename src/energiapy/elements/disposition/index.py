"""Index gives the disposition of Program Elements (Variables, Parameters, Constraints)
"""

from dataclasses import dataclass, field, fields

from sympy import Idx, symbols

from ...components.analytical.player import Player
from ...components.commodity.cash import Cash
from ...components.commodity.emission import Emission
from ...components.commodity.land import Land
from ...components.commodity.material import Material
from ...components.commodity.resource import Resource
from ...components.operation.process import Process
from ...components.operation.storage import Storage
from ...components.operation.transit import Transit
from ...components.scope.spatial.linkage import Linkage
from ...components.scope.spatial.location import Location
from ...components.scope.spatial.network import Network
from ...components.scope.temporal.mode import X
from ...components.scope.temporal.scale import Scale
from ...core._handy._dunders import _Dunders
from ...core.aliases.cmps.iscmp import IsCmp


@dataclass
class Index(_Dunders):
    """The spatiotemporal disposition of the Component
    Index is the index of the a Program Model Element
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

    # Do not reorder these fields, Please
    ply: Player = field(default=None)
    emn: Emission = field(default=None)
    csh: Cash = field(default=None)
    res: Resource = field(default=None)
    mat: Material = field(default=None)
    lnd: Land = field(default=None)
    pro: Process = field(default=None)
    stg: Storage = field(default=None)
    trn: Transit = field(default=None)
    loc: Location = field(default=None)
    lnk: Linkage = field(default=None)
    ntw: Network = field(default=None)
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

    def idx(self):
        """Gives the full disposition list, by expanding the temporal index"""
        return [
            (*[k.name for k in self.disposition[:-1]], *t) for t in self.scl.index if t
        ]

    def structure(self):
        """provides the structure of the Index"""
        return [f.name for f in fields(self) if getattr(self, f.name)]

    def childless(self, child: IsCmp):
        """Gives a disposition without the component"""
        return {
            f.name: getattr(self, f.name)
            for f in fields(self)
            if not isinstance(getattr(self, f.name), child)
        }

    def __len__(self):
        return len(self.scl)

    @property
    def sym(self):
        """Symbol"""
        return symbols(",".join([f'{d}' for d in self.disposition]), cls=Idx)
