"""DataSet is a deterministic data given to account for temporal variability in parameter.
Created when input is a DataFrame
"""

from dataclasses import dataclass, field
from operator import is_

from pandas import DataFrame
from sympy import IndexedBase

from ..disposition.bound import VarBnd
from ._value import _Value


@dataclass
class DataSet(_Value):
    """Variable data set"""

    data: DataFrame = field(default=None)

    def __post_init__(self):
        _Value.__post_init__(self)
        # Data has to be provided as a DataFrame
        if not isinstance(self.data, DataFrame):
            raise ValueError(f'{self.name}: please provide DataFrame')

        # Data is made into a dictionary with the keys being the indices of the scale
        # will look something like {(0,0): 4, (0,1): 9, (1,0): 2}
        self.data = self.data[self.data.columns[0]].to_dict()
        self.data = {
            self.index.scl.index[i]: self.data[i] for i in range(len(self.data))
        }

    @property
    def value(self) -> dict:
        """Returns a dictionary of data"""
        return self.data

    @property
    def id(self):
        """Symbol"""
        return IndexedBase(f'DtSt{self.varbnd.value}{self.spclmt.value}')

    @staticmethod
    def collection():
        """reports what collection the component belongs to"""
        return 'datasets'

    # DataSet are compared on the basis of what bound they are
    def __lt__(self, other):
        if isinstance(other, (int, float)) and is_(self.varbnd, VarBnd.UB):
            return False
        elif isinstance(other, DataSet) and is_(other.varbnd, VarBnd.LB):
            return False
        else:
            return True

    def __gt__(self, other):
        if isinstance(other, (int, float)) and is_(self.varbnd, VarBnd.UB):
            return True
        elif isinstance(other, DataSet) and is_(other.varbnd, VarBnd.LB):
            return True
        else:
            return False
