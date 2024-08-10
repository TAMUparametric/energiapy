from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import TYPE_CHECKING

from .._core._handy._dunders import _Dunders

from pandas import DataFrame

from ..values.constant import Constant
from ..values.dataset import DataSet
from ..values.m import M
from ..values.theta import Theta
from .disposition import Disposition

from ..components.analytical.player import Player
from ..components.asset.cash import Cash
from ..components.asset.land import Land
from ..components.commodity.material import Material
from ..components.commodity.resource import Resource
from ..components.impact.emission import Emission
from ..components.operational.process import Process
from ..components.operational.storage import Storage
from ..components.operational.transit import Transit
from ..components.temporal.scale import Scale
from ..components.scope.network import Network
from ..components.spatial.location import Location
from ..components.spatial.linkage import Linkage
from ..funcs.utils.dictionary import get_depth

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
    from .._core._aliases._is_input import IsSptTmpInput, IsBaseInput


@dataclass
class _DataPoint(_Dunders):
    """Is a particular data point"""

    # Do not reorder these fields
    base_input: IsBaseInput = field(default=None)
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

        self.disposition = Disposition(
            {i.name: getattr(self, i.name) for i in fields(self)}
        )


@dataclass
class _SptTmpInput:
    """Is a spatial temporal input"""

    name_attr: str = field(default=None)
    dict_input: IsSptTmpInput = field(default=None)

    def __post_init__(self):

        self.update_dict_input()

    def update_dict_input(self) -> dict:
        """Makes Dict[Disposition, IsBaseInput] from IsSptTmpInput"""
        dict_input_upd = {}

        def update_dispositions(dict_input: dict):
            """Updates the dispositions"""

            nonlocal dict_input_upd

            if isinstance(dict_input, dict):
                for i, j in dict_input.items():
                    if isinstance(i, Player):
                        ply = i
                    if isinstance(i, Emission):
                        emn = i
                    if isinstance(i, Cash):
                        csh = i
                    if isinstance(i, Resource):
                        res = i
                    if isinstance(i, Material):
                        mat = i
                    if isinstance(i, Land):
                        lnd = i
                    if isinstance(i, Process):
                        pro = i
                    if isinstance(i, Storage):
                        stg = i
                    if isinstance(i, Transit):
                        trn = i
                    if isinstance(i, Location):
                        loc = i
                    if isinstance(i, Linkage):
                        lnk = i
                    if isinstance(i, Network):
                        ntw = i
                    if isinstance(i, Scale):
                        scl = i

                    if isinstance(j, dict):
                        update_dispositions(j)

                    else:
                        dp = j
                    disp = Disposition(
                        ply, emn, csh, res, mat, lnd, pro, stg, trn, loc, lnk, ntw, scl
                    )

                    dict_input_upd[disp] = dp

        update_dispositions(self.dict_input)

        setattr(self, 'dict_input', dict_input_upd)


@dataclass
class _CmpData(_Dunders):
    """Is Component Data"""

    name_cmp: str = field(default=None)

    def __post_init__(self):
        self.name = f'CmpData|{self.name_cmp}|'

    def __setattr__(self, name, spttmpinput: _SptTmpInput):

        for disposition, datapoint in spttmpinput.dict_input.items():

            if isinstance(datapoint, (list, tuple)):
                datapoint = [self.birth_value(disposition, i) for i in datapoint]

            else:
                datapoint = self.birth_value(disposition, datapoint)

            spttmpinput.dict_input[disposition] = datapoint

        super().__setattr__(name, spttmpinput.dict_input)

    def birth_value(self, disposition: Disposition, value: IsBaseInput) -> IsBaseInput:
        """Creates a value"""
        if isinstance(value, (float, int)) and not isinstance(value, bool):
            datapoint = Constant(constant=value, disposition=disposition)

        if isinstance(value, bool):
            datapoint = M(big=value, disposition=disposition)

        if isinstance(value, DataFrame):
            datapoint = DataSet(data=value, disposition=disposition)

        if isinstance(value, tuple):
            datapoint = Theta(space=value, disposition=disposition)

        # if passing a BigM or Th, update
        if hasattr(value, 'big') or hasattr(value, 'space'):
            for i, j in disposition.args().items():
                setattr(value, i, j)
            datapoint = value

        return datapoint

    # def data(self):
    #     """prints out the data"""
    #     return self._data


@dataclass
class Data(_Dunders):
    """Is the data required for the model"""

    name: str = field(default=None)

    def __post_init__(self):
        self.name = f'Data|{self.name}|'
        self.constants, self.ms, self.thetas, self.datasets = ([] for _ in range(4))

    def __setattr__(self, name, value: _CmpData):

        setattr(self, value.name_cmp, value)

        super().__setattr__(name, value)
