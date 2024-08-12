from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from pandas import DataFrame

from .._core._handy._dunders import _Dunders
from ..components.analytical.player import Player
from ..components.asset.cash import Cash
from ..components.asset.land import Land
from ..components.commodity.material import Material
from ..components.commodity.resource import Resource
from ..components.impact.emission import Emission
from ..components.operational.process import Process
from ..components.operational.storage import Storage
from ..components.operational.transit import Transit
from ..components.scope.network import Network
from ..components.spatial.linkage import Linkage
from ..components.spatial.location import Location
from ..components.temporal.scale import Scale
from ..components._base._defined import _Defined
from ..values.constant import Constant
from ..values.dataset import DataSet
from ..values.m import M
from ..values.theta import Theta
from .disposition import Disposition

if TYPE_CHECKING:
    from .._core._aliases._is_component import (
        IsCash,
        IsEmission,
        IsLand,
        IsLinkage,
        IsLocation,
        IsMaterial,
        IsNetwork,
        IsPlayer,
        IsProcess,
        IsResource,
        IsScale,
        IsStorage,
        IsTransit,
    )
    from .._core._aliases._is_input import IsBaseInput, IsSptTmpInput


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
                dict_input = {
                    (spt, tmp): val
                    for spt, tmpdict in dict_input.items()
                    for tmp, val in tmpdict.items()
                }
                
                for spttmp in dict_input.keys():

                    if isinstance(spttmp[0], Location):
                        loc = spttmp[0]
                    if isinstance(spttmp[0], Linkage):
                        lnk = spttmp[0]
                    if isinstance(spttmp[0], Network):
                        ntw = spttmp[0]
                    if isinstance(spttmp[1], Scale):
                        scl = spttmp[1]

                    val = dict_input[spttmp]
                    
                    if isinstance(val, Emission):
                        emn = val
                    if isinstance(val, Cash):
                        csh = val
                    if isinstance(val, Resource):
                        res = val
                    if isinstance(val, Material):
                        mat = val
                    if isinstance(val, Land):
                        lnd = val
                    if isinstance(val, Process):
                        pro = val
                    if isinstance(val, Storage):
                        stg = val
                    if isinstance(val, Transit):
                        trn = val

                    if isinstance(val, dict):
                        update_dispositions(val)

                    else:
                        dp = val

                    disp = Disposition(
                        emn,
                        csh,
                        res,
                        mat,
                        lnd,
                        pro,
                        stg,
                        trn,
                        loc,
                        lnk,
                        ntw,
                        scl,
                    )
                    print('disp', disp)

                    dict_input_upd[disp] = dp

        update_dispositions(self.dict_input)

        setattr(self, 'dict_input', dict_input_upd)


@dataclass
class CmpData(_Dunders):
    """Is Component Data"""

    name_cmp: str = field(default=None)

    def __post_init__(self):
        self.name = f'CmpData|{self.name_cmp}|'

    def __setattr__(self, name, dict_input):

        spttmpinput = _SptTmpInput(name, dict_input)

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


@dataclass
class Data(_Dunders):
    """Is the data required for the model"""

    name: str = field(default=None)

    def __post_init__(self):
        self.name = f'Data|{self.name}|'
        self.constants, self.ms, self.thetas, self.datasets = ([] for _ in range(4))

    def __setattr__(self, name, value):

        if issubclass(type(value), _Defined):
            setattr(self, value.name_cmp, value)

        super().__setattr__(name, value)
