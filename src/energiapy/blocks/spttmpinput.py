"""SpatioTemporalInput, this is an intermediate class
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Tuple

from ..components.analytical.player import Player
from ..components.commodity.cash import Cash
from ..components.commodity.emission import Emission
from ..components.commodity.land import Land
from ..components.commodity.material import Material
from ..components.commodity.resource import Resource
from ..components.operational.process import Process
from ..components.operational.storage import Storage
from ..components.operational.transit import Transit
from ..components.scope.network import Network
from ..components.spatial.linkage import Linkage
from ..components.spatial.location import Location
from ..components.temporal.scale import Scale
from ..core._handy._dunders import _Dunders
from ..disposition.disposition import Disposition
from ..parameters.designators.mode import X
from ..utils.dictionary import flatten

if TYPE_CHECKING:
    from ..core.aliases.is_component import IsComponent
    from ..core.aliases.is_input import IsSptTmpInp
    from ..core.aliases.is_value import IsValue


@dataclass
class SptTmpInp(_Dunders):
    """This containts the dictionary of input in a particular format

    This is made in Data Model Class, and is used in Scenario class

    The format is like this:
    * - optional


    {Spatial/Network: {Scale: {*Mode: {*Operational: {*Commodity: value}}}}}

    This ensures consistence in the input once provided to the Scenario class

    The Disposition is also determined here and set as the key in the dictionary

    """

    name_attr: str = field(default=None)
    dict_input: IsSptTmpInp = field(default=None)

    def __post_init__(self):
        # The original dictionary input
        # keep it because some operations birth processes
        # processes need the og input
        self.og_input = self.dict_input
        self.update_dict_input()

    @property
    def dispositions(self):
        """Returns the Disposition of the input"""
        return list(self.dict_input.keys())

    @property
    def name(self):
        """Returns the Disposition of the input"""
        return f'{self.name_attr}{self.dict_input}'

    @property
    def by_position(self):
        """Returns the Disposition of the input"""
        return {i: val for i, val in enumerate(list(self.dict_input.values()))}

    def update_dict_input(self):
        """Updates the dict_input
        Returns:
            dict: {Disposition: value}
        """
        # Flatten the dictionary. Now the keys are tuples
        # {(Network/Spatial, Scale, ...): value}
        dict_iter = flatten(self.dict_input)
        dict_upd = {}

        for key, val in dict_iter.items():

            ply, emn, csh, res, mat, lnd, pro, stg, trn, loc, lnk, ntw, scl, mde = (
                None for _ in range(14)
            )

            if not isinstance(key, tuple):
                raise ValueError(
                    f'Something is wrong with the input at {self}. If providing dict, check structure'
                )
            # Check if a particular Component has been declared
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
                if isinstance(cmp, X):
                    mde = cmp

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
                mde=mde,
            )

            dict_upd[disp] = val

        # update the input with a dictionary {Disposition: value}
        self.dict_input = dict_upd

    def get(self, index: Tuple[IsComponent] = None, position: int = None) -> IsValue:
        """Gets the value of the input at the index
        You can give the index or the position
        or nothing, to get some guidelines
        if both are given, will use the index

        Args:
            index (tuple, optional): Index to get the value
            position (int, optional): Position to get the value. Defaults to None

        Returns:
            IsValue: The value at the index
        """

        def siren_position():
            print()
            print('For position, use this as a guideline:')
            print(f'{self.by_position}')
            print('Or just use the by_position property')

        def siren_index():
            print()
            print('For index, use this as a guideline')
            print(f'{self.dict_input}')

        if not index and not position:
            print('No index or position provided')
            siren_position()
            siren_index()

        if position and not index:
            if position > len(self.dispositions):
                print(f'Position {position} out of range')
                siren_position()
            else:
                index = self.dispositions[position]
                return self.dict_input[index]

        if index and not position:
            if not index in [disp.index for disp in self.dispositions]:
                print(f'Index {index} not found')
                siren_index()

            for disp, value in self.dict_input.items():
                if disp.index == index:
                    return value

        if index and position:
            print('Provide either index or position, not both')
            print('If you provide both, the index will be used')
            return self.get(index=index)
