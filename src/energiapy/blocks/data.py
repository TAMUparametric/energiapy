"""Data Model Block
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List

from pandas import DataFrame

from .._core._handy._dunders import _Dunders
from ..disposition.bounds import SpcLmt, VarBnd
from ..parameters.designators.incidental import I
from ..parameters.values.constant import Constant
from ..parameters.values.dataset import DataSet
from ..parameters.values.m import M
from ..parameters.values.theta import Theta
from ._base._block import _Block
from ._base._spttmpinput import _SptTmpInput

if TYPE_CHECKING:
    from .._core._aliases._is_block import IsDisposition
    from .._core._aliases._is_component import IsDefined
    from .._core._aliases._is_input import IsBaseInput
    from .._core._aliases._is_value import IsSpcLmt, IsValue, IsVarBnd


@dataclass
class DataBlock(_Dunders):
    """Component Data Block
    Recieves data for component from attributes
    Converts it to one of the internal formats (M, Constant, DataSet, Theta)
    Also determines the bounds (VarBnd, SpcLmt) of the data

    Each Component has a DataBlock which is then held in Data class

    Data and the Bounds are used to make Parameters, Variables, and enventually Constraints

    Args:
        component (IsDefined): The component to which the data belongs.
    """

    component: IsDefined = field(default=None)

    def __post_init__(self):
        self.name = f'Data|{self.component}|'

    def __setattr__(self, name, value):

        spclmts = [SpcLmt.START, SpcLmt.END]
        varbnds = [VarBnd.LB, VarBnd.UB]

        if isinstance(value, dict):
            # _Spt holds the data in a particular format
            # {Disposition: value}. The disposition is made there
            # This is only temporary and the user eventually sees a list of parameters
            spttmpinput = _SptTmpInput(name, value)

            for disposition, datapoint in spttmpinput.dict_input.items():
                if isinstance(datapoint, list):
                    if len(datapoint) == 1:
                        # if only one value, the value given is an upper bound
                        datapoint = [0] + datapoint
                    # The first value becomes the LB, and the second becomes the UB
                    datapoint = [
                        self.birth_value(disposition, i, varbnd=varbnds[b])
                        for b, i in enumerate(datapoint)
                    ]

                elif isinstance(datapoint, tuple):
                    # Tuples used to declare Theta space can have DataFrames as values
                    datapoint = tuple(
                        [
                            self.birth_value(disposition, i, spclmt=spclmts[b])
                            for b, i in enumerate(datapoint)
                        ]
                    )

                    # Not BigMs though, so cannot have True in the tuple
                    if any(isinstance(i, M) for i in datapoint):
                        raise ValueError(
                            'Parametric space cannot extent to BigM (No True)'
                        )

                    # A Theta variable can be declared now
                    datapoint = self.birth_value(disposition, datapoint)

                elif isinstance(datapoint, set):

                    # A set is only used when there can be an incidental parameter
                    # capex, opex for example
                    datapoint = {self.birth_value(disposition, i) for i in datapoint}

                else:
                    # if not compound (set, list, tuple)
                    datapoint = self.birth_value(disposition, datapoint)

                # Now update the value with an internal value type
                spttmpinput.dict_input[disposition] = datapoint
            # Sort the values by length
            
            value = sorted(spttmpinput.dict_input.values(), key=len)
            print('dp', datapoint)
            print(len(datapoint))
            print('v', value)

        super().__setattr__(name, value)

    @property
    def attrs(self) -> List[str]:
        """Returns the defined attributes of the component

        Returns:
            List[str]: list of attributes
        """
        return [i for i in self.component.inputs() if getattr(self.component, i)]

    @property
    def ms(self):
        """Returns the Ms"""
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

    def fetch(self, data: IsValue) -> List[IsValue]:
        """Fetches input data of a particular type

        Args:
            data (IsValue): The type of values to fetch [M, Constant, DataSet, Theta]

        Returns:
            List[IsValue]: List of values (M, Constant, DataSet, Theta)
        """

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
    ) -> IsValue:
        """Creates a parameter value

        Args:
            disposition (IsDisposition): The disposition of the value
            value (IsBaseInput): The input value used to make an internal value, like M, Constant, DataSet, Theta
            varbnd (IsVarBnd): The variable bound (lower, upper)
            spclmt (IsSpcLmt): The parametric space limit (start, end)

        Returns:
            IsValue: Internal datatype value (M, Constant, DataSet, Theta)

        """

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
    """Is the data required for the Model

    set attribures are DataBlock objects

    Attributes:
        name (str): name, takes from the name of the Scenario

    """

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

    def fetch(self, data: str) -> List[IsValue]:
        """Fetches input data of a particular type
        Args:
            data: str: The type of data to fetch [thetas, ms, constants, datasets]
        """
        return sum([getattr(getattr(self, i), data) for i in self.components()], [])
