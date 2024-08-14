from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ...components.analytical.player import Player
from ...components.commodity.cash import Cash
from ...components.commodity.land import Land
from ...components.commodity.material import Material
from ...components.commodity.resource import Resource
from ...components.impact.emission import Emission
from ...components.operational.process import Process
from ...components.operational.storage import Storage
from ...components.operational.transit import Transit
from ...components.scope.network import Network
from ...components.spatial.linkage import Linkage
from ...components.spatial.location import Location
from ...components.temporal.scale import Scale
from ...disposition.disposition import Disposition
from ...funcs.utils.dictionary import flatten

if TYPE_CHECKING:
    from ..._core._aliases._is_input import IsSptTmpInput


@dataclass
class _SptTmpInput:
    """Is a spatial temporal input"""

    name_attr: str = field(default=None)
    dict_input: IsSptTmpInput = field(default=None)

    def __post_init__(self):

        self.update_dict_input()

    def update_dict_input(self):
        """Updates the dict_input
        makes the form, {Disposition: value}
        """
        dict_iter = flatten(self.dict_input)
        dict_upd = {}

        for key, val in dict_iter.items():

            ply, emn, csh, res, mat, lnd, pro, stg, trn, loc, lnk, ntw, scl = (
                None for _ in range(13)
            )

            if not isinstance(key, tuple):
                raise ValueError(
                    f'Something is wrong with the input at {self}. If providing dict, check structure'
                )

            for cmp in key:
                if isinstance(cmp, Player):
                    ply = cmp
                if isinstance(cmp, Emission):
                    emn = cmp
                if isinstance(cmp, Cash):
                    csh = cmp
                if isinstance(cmp, Resource):
                    res = cmp
                if isinstance(cmp, Material):
                    mat = cmp
                if isinstance(cmp, Land):
                    lnd = cmp
                if isinstance(cmp, Process):
                    pro = cmp
                if isinstance(cmp, Storage):
                    stg = cmp
                if isinstance(cmp, Transit):
                    trn = cmp
                if isinstance(cmp, Location):
                    loc = cmp
                if isinstance(cmp, Linkage):
                    lnk = cmp
                if isinstance(cmp, Network):
                    ntw = cmp
                if isinstance(cmp, Scale):
                    scl = cmp

            disp = Disposition(
                ply=ply,
                emn=emn,
                csh=csh,
                res=res,
                mat=mat,
                lnd=lnd,
                pro=pro,
                stg=stg,
                trn=trn,
                loc=loc,
                lnk=lnk,
                ntw=ntw,
                scl=scl,
            )

            dict_upd[disp] = val
        self.dict_input = dict_upd
