"""Component Block of the Data Rendition of the Model
"""

from dataclasses import dataclass, field

from pandas import DataFrame

from ..core._handy import _Dunders
from ..core.isalias.cmps.isdfn import IsDfn
from ..core.isalias.elms import IsVal
from ..core.isalias.inps.isinp import IsInp
from ..core.nirop.errors import InputTypeError
from ..elements.index import Idx
from ..elements import Constant
from ..elements import DataSet
from ..elements.m import M
from ..elements.theta import Theta
from .datum import Datum


@dataclass
class Data(_Dunders):
    """Component Data Block
    Recieves data for component from attributes
    Converts it to one of the internal formats (M, Constant, DataSet, Theta)
    Also determines the bounds (VarBnd, SpcLmt) of the data

    Each Component has a DataBlock which is then held in Data class

    Data and the Bounds are used to make Parameters, Variables, and enventually Constraints

    Args:
        component (IsDfn): The component to which the data belongs.
        m (float): small m value

    """

    component: IsDfn = field(default=None)
    m: float = field(default=None)

    def __post_init__(self):
        self.name = f'Data|{self.component}|'
        # this will have the attributes of the components as keys
        # will be set back into the component
        self.data = {}

    def __setattr__(self, name, value):

        spclmts = [SpcLmt.START, SpcLmt.END]
        varbnds = [VarBnd.LB, VarBnd.UB]

        if isinstance(value, dict) and not name == 'data':
            # _Spt holds the data in a particular format
            # {Idx: value}. The disposition is made there
            # This is only temporary and the user eventually sees a list of parameters
            datum = Datum(attr=name, data=value, component=self.component)
            for index, datapoint in datum.data.items():

                if datapoint is True:
                    # if datapoint is True, put it in a list
                    # it will become an upper bound in the next step
                    datapoint = [True]

                if isinstance(datapoint, list):
                    if len(datapoint) == 1:
                        # if only one value, the value given is an upper bound
                        datapoint = [0] + datapoint
                    # The first value becomes the LB, and the second becomes the UB
                    datapoint = [
                        self.birth_value(index, i, varbnd=varbnds[b])
                        for b, i in enumerate(datapoint)
                    ]

                elif isinstance(datapoint, tuple):
                    # Tuples used to declare Theta space can have DataFrames as values
                    datapoint = tuple(
                        [
                            self.birth_value(index, i, spclmt=spclmts[b])
                            for b, i in enumerate(datapoint)
                        ]
                    )

                    # Not BigMs though, so cannot have M with big = True in the tuple
                    if any(i.big for i in datapoint if isinstance(i, M)):
                        raise InputTypeError(
                            'Parametric space cannot extent to BigM (No True)',
                            self.component,
                            name,
                            datapoint,
                        )

                    # A Theta variable can be declared now
                    datapoint = self.birth_value(index, datapoint)

                elif isinstance(datapoint, set):

                    # A set is only used when there can be an incidental parameter
                    # capex, opex for example
                    datapoint = {self.birth_value(index, i) for i in datapoint}

                else:
                    # if not compound (set, list, tuple)
                    datapoint = self.birth_value(index, datapoint)

                # Now update the value with an internal value type
                datum.data[index] = datapoint
            # Sort the values by length
            value = sorted(datum.data.values(), key=len)

            self.data[name] = datum

        super().__setattr__(name, value)

    @property
    def attrs(self) -> list[str]:
        """Returns the defined attributes of the component

        Returns:
            list[str]: list of attributes
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

    def fetch(self, data: IsVal) -> list[IsVal]:
        """Fetches input data of a particular type

        Args:
            data (IsValue): The type of values to fetch [M, Constant, DataSet, Theta]

        Returns:
            list[IsValue]: list of values (M, Constant, DataSet, Theta)
        """

        data_list = []

        for attr in self.attrs:
            attr_data = getattr(self, attr)
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
        index: Idx,
        value: IsInp,
        varbnd: VarBnd = None,
        spclmt: SpcLmt = None,
    ) -> IsVal:
        """Creates a parameter value

        Args:
            index (IsIndex): The index of the value
            value (IsBaseInput): The input value used to make an internal value, like M, Constant, DataSet, Theta
            varbnd (IsVarBnd): The variable bound (lower, upper)
            spclmt (IsSpcLmt): The parametric space limit (start, end)

        Returns:
            IsValue: Internal datatype value (M, Constant, DataSet, Theta)

        """

        args = {
            'index': index,
            'varbnd': varbnd,
            'spclmt': spclmt,
        }

        if isinstance(value, I):
            value = value.value
            incdntl = True
        else:
            incdntl = False
        if isinstance(value, (float, int)) and not isinstance(value, bool):
            # if small m is provided, make a small m instead of 0
            if self.m and value == 0:
                datapoint = M(big=False, m=self.m, **args)
            else:
                datapoint = Constant(constant=value, **args, incdntl=incdntl)

        if isinstance(value, bool):
            datapoint = M(big=value, **args)

        if isinstance(value, DataFrame):
            datapoint = DataSet(data=value, **args, incdntl=incdntl)

        if isinstance(value, tuple):
            datapoint = Theta(space=value, **args)

        # if passing a BigM or Th, update
        if hasattr(value, 'big') or hasattr(value, 'space'):
            for i, j in index.args().items():
                setattr(value, i, j)
            datapoint = value

        return datapoint