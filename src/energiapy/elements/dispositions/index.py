"""Index is attached to parameters, variables, and constraints
"""

from dataclasses import dataclass, field, fields

from sympy import Idx, symbols

from ...core._handy._dunders import _Dunders

from ...core.aliases.iscmp import IsCmp
from ...components.analytical.player import Player
from ...components.commodity.cash import Cash
from ...components.commodity.emission import Emission
from ...components.commodity.land import Land
from ...components.commodity.material import Material
from ...components.commodity.resource import Resource
from ...components.operational.process import Process
from ...components.operational.storage import Storage
from ...components.operational.transit import Transit
from ...components.scope.network import Network
from ...components.spatial.linkage import Linkage
from ...components.spatial.location import Location
from ...components.temporal.scale import Scale
from ...components.temporal.mode import X


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

    # Do not reorder these fields
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

        # this is the component index
        self.disposition = tuple(
            [getattr(self, f.name) for f in fields(self) if getattr(self, f.name)]
        )

        # this maintains the order of the components in the index
        self.name = f'{tuple(dict.fromkeys(self.disposition).keys())}'

    def args(self):
        """provides a dict of attributes"""
        return {f.name: getattr(self, f.name) for f in fields(self)}

    def idx(self):
        """Gives the full index list, by expanding the temporal index"""
        return [
            (*[k.name for k in self.disposition[:-1]], *j)
            for j in self.scl.disposition
            if j
        ]

    def structure(self):
        """provides the structure of the disposition"""
        return [i.name for i in fields(self) if getattr(self, i.name)]

    def childless(self, child: IsCmp):
        """Gives the disposition with the component removed"""
        return {
            f.name: getattr(self, f.name)
            for f in fields(self)
            if not isinstance(getattr(self, f.name), child)
        }

    def scaledown(self):
        """Goes to a lower scale"""
        return Index(**self.args())

    def __len__(self):
        return len(self.scl)

    @property
    def sym(self):
        """Symbol"""
        return symbols(",".join([f'{i}' for i in self.disposition]), cls=Idx)
