from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List

from pandas import DataFrame

from .._core._handy._dunders import _Dunders
from ._base._block import _Block
from ..parameters.bounds import SpcLmt, VarBnd
from ..parameters.data.constant import Constant
from ..parameters.data.dataset import DataSet
from ..parameters.data.m import M
from ..parameters.data.theta import Theta
from ..parameters.designators.incidental import I
from ._base._spttmpinput import _SptTmpInput

if TYPE_CHECKING:
    from .._core._aliases._is_data import IsData, IsVarBnd, IsSpcLmt
    from .._core._aliases._is_input import IsBaseInput
    from .._core._aliases._is_block import IsDisposition
    from .._core._aliases._is_component import IsComponent


@dataclass
class DataBlock(_Dunders):
    """Is Component Data"""

    component: IsComponent = field(default=None)

    def __post_init__(self):
        self.name = f'Data|{self.component}|'

    def __setattr__(self, name, value):

        spclmts = [SpcLmt.START, SpcLmt.END]
        varbnds = [VarBnd.LOWER, VarBnd.UPPER]

        if isinstance(value, dict):
            spttmpinput = _SptTmpInput(name, value)

            for disposition, datapoint in spttmpinput.dict_input.items():
                if isinstance(datapoint, list):
                    datapoint = [
                        self.birth_value(disposition, i, varbnd=varbnds[b])
                        for b, i in enumerate(datapoint)
                    ]

                elif isinstance(datapoint, tuple):
                    datapoint = tuple(
                        [
                            self.birth_value(disposition, i, spclmt=spclmts[b])
                            for b, i in enumerate(datapoint)
                        ]
                    )

                    datapoint = self.birth_value(disposition, datapoint)

                elif isinstance(datapoint, set):
                    datapoint = {self.birth_value(disposition, i) for i in datapoint}

                else:
                    datapoint = self.birth_value(disposition, datapoint)

                spttmpinput.dict_input[disposition] = datapoint

            value = sorted(spttmpinput.dict_input.values(), key=len)

        super().__setattr__(name, value)

    @property
    def attrs(self):
        """Returns the defined attribures of the component"""
        return [i for i in self.component.inputs() if getattr(self.component, i)]

    @property
    def ms(self):
        """Returns the M"""
        return self.fetch(M)

    @property
    def constants(self):
        """Returns the Constants"""
        return self.fetch(Constant)

    @property
    def datasets(self):
        """Returns the DataSets"""
        return self.fetch(DataSet)

    @property
    def thetas(self):
        """Returns the Thetas"""
        return self.fetch(Theta)

    @property
    def all(self):
        """Returns all data"""
        return self.ms + self.constants + self.datasets + self.thetas

    def fetch(self, data: IsData) -> List[IsData]:
        """Fetches input data of a particular type"""

        data_list = []

        for i in self.attrs:
            attr_data = getattr(self, i)
            for d in attr_data:
                if isinstance(d, data):
                    data_list.append(d)
                elif isinstance(d, (set, list, tuple)):
                    for j in d:
                        if isinstance(j, data):
                            data_list.append(j)
        return sorted(data_list)

    def birth_value(
        self,
        disposition: IsDisposition,
        value: IsBaseInput,
        varbnd: IsVarBnd = None,
        spclmt: IsSpcLmt = None,
    ) -> IsBaseInput:
        """Creates a parameter value"""

        args = {
            'disposition': disposition,
            'varbnd': varbnd,
            '_spclmt': spclmt,
        }

        if isinstance(value, I):
            value = value.value
            incdntl = True
        else:
            incdntl = False

        if isinstance(value, (float, int)) and not isinstance(value, bool):
            datapoint = Constant(constant=value, **args, incdntl=incdntl)

        if isinstance(value, bool):
            datapoint = M(big=value, **args)

        if isinstance(value, DataFrame):
            datapoint = DataSet(data=value, **args, incdntl=incdntl)

        if isinstance(value, tuple):
            datapoint = Theta(space=value, **args)

        # if passing a BigM or Th, update
        if hasattr(value, 'big') or hasattr(value, 'space'):
            for i, j in disposition.args().items():
                setattr(value, i, j)
            datapoint = value

        return datapoint


@dataclass
class Data(_Block):
    """Is the data required for the model"""

    name: str = field(default=None)

    def __post_init__(self):
        _Block.__post_init__(self)
        self.name = f'Data|{self.name}|'

    @property
    def ms(self):
        """Returns the M"""
        return self.fetch('ms')

    @property
    def constants(self):
        """Returns the Constants"""
        return self.fetch('constants')

    @property
    def datasets(self):
        """Returns the DataSets"""
        return self.fetch('datasets')

    @property
    def thetas(self):
        """Returns the Thetas"""
        return self.fetch('thetas')

    @property
    def all(self):
        """Returns all data"""
        return self.ms + self.constants + self.datasets + self.thetas

    def fetch(self, data: str) -> List[IsData]:
        """Fetches input data of a particular type
        Args:
            data: str: The type of data to fetch [thetas, ms, constants, datasets]
        """
        return sum([getattr(getattr(self, i), data) for i in self.components()], [])
