from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from pandas import DataFrame

from .._core._handy._dunders import _Dunders
from ..disposition.disposition import Disposition
from ..parameters.bounds import SpcLmt, VarBnd
from ..parameters.data.constant import Constant
from ..parameters.data.dataset import DataSet
from ..parameters.data.m import M
from ..parameters.data.theta import Theta
from ..parameters.designators.incidental import I
from ._base._spttmpinput import _SptTmpInput

if TYPE_CHECKING:
    from .._core._aliases._is_data import IsData
    from .._core._aliases._is_input import IsBaseInput


@dataclass
class DataBlock(_Dunders):
    """Is Component Data"""

    component: str = field(default=None)

    def __post_init__(self):
        self.name = f'Data|{self.component}|'
        self.constants, self.ms, self.thetas, self.datasets = ([] for _ in range(4))
        self.attrs = []

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

                self.add(datapoint)

            self.attrs.append(name)

            value = sorted(spttmpinput.dict_input.values(), key=len)

        super().__setattr__(name, value)

    def birth_value(
        self,
        disposition: Disposition,
        value: IsBaseInput,
        varbnd: VarBnd = None,
        spclmt: SpcLmt = None,
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

    def add(self, datapoint: IsData):
        """Updates the collection lists of values for the component block

        Args:
            datapoint (IsData): the data to be added to a particular collection
        """

        if isinstance(datapoint, (list, tuple, set)):
            for dp in datapoint:
                self.add(dp)

        else:
            list_curr = getattr(self, datapoint.collection())
            setattr(self, datapoint.collection(), sorted(set(list_curr) | {datapoint}))


@dataclass
class Data(_Dunders):
    """Is the data required for the model"""

    name: str = field(default=None)

    def __post_init__(self):
        self.name = f'Data|{self.name}|'
