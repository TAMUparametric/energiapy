from __future__ import annotations

from dataclasses import dataclass, field
from operator import is_
from typing import TYPE_CHECKING

from pandas import DataFrame

from .._core._handy._dunders import _Dunders
from ..parameters.bounds import SpcLmt, VarBnd
from ..parameters.constant import Constant
from ..parameters.dataset import DataSet
from ..parameters.m import M
from ..parameters.theta import Theta
from ._spttmpinput import _SptTmpInput
from .disposition import Disposition

if TYPE_CHECKING:
    from .._core._aliases._is_data import IsData
    from .._core._aliases._is_input import IsBaseInput


@dataclass
class CmpData(_Dunders):
    """Is Component Data"""

    name_cmp: str = field(default=None)

    def __post_init__(self):
        self.name = f'Data|{self.name_cmp}|'
        self.constants, self.ms, self.thetas, self.datasets = ([] for _ in range(4))

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

                else:
                    datapoint = self.birth_value(disposition, datapoint)

                spttmpinput.dict_input[disposition] = datapoint

                self.add(datapoint)
            # value = spttmpinput.dict_input
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
            '_varbnd': varbnd,
            '_spclmt': spclmt,
        }

        if isinstance(value, (float, int)) and not isinstance(value, bool):
            datapoint = Constant(constant=value, **args)

        if isinstance(value, bool):
            datapoint = M(big=value, **args)

        if isinstance(value, DataFrame):
            datapoint = DataSet(data=value, **args)

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

        if isinstance(datapoint, (list, tuple)):
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
        self.compdata = []

    def __setattr__(self, name, value):

        if isinstance(value, CmpData):
            self.compdata.append(value)

        super().__setattr__(name, value)

    @property
    def datasets(self):
        """Returns the DataSets"""
        return [i for i in self.compdata if is_(i.collection(), 'datasets')]

    @property
    def ms(self):
        """Returns the Ms"""
        return [i for i in self.compdata if is_(i.collection(), 'ms')]

    @property
    def thetas(self):
        """Returns the Thetas"""
        return [i for i in self.compdata if is_(i.collection(), 'thetas')]

    @property
    def constants(self):
        """Returns the Constants"""
        return [i for i in self.compdata if is_(i.collection(), 'constants')]
