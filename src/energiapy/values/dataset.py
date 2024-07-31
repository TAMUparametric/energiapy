"""DataSet is a deterministic data given to account for temporal variability in parameter.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from operator import is_
from typing import TYPE_CHECKING

from pandas import DataFrame
from sklearn.preprocessing import MinMaxScaler, StandardScaler

# from ..core.base import Dunders
from .value import Value
from .bound import Bound

if TYPE_CHECKING:
    from ..components.horizon import Horizon
    from ..type.alias import IsAspect, IsComponent, IsIndex, IsData, IsDeclaredAt


@dataclass
class DataSet(Value):
    data: IsData = field(default=None)
    
    def __post_init__(self):
        # Data has to be provided as a DataFrame
        if not isinstance(self.data, DataFrame):
            raise ValueError(
                ': please provide DataFrame')
            # TODO - complete this
        
        # Find the Scale that matches the length and set tuple index accordingly
        # TODO - Push outside
        # if len(self.data) in self.horizon.n_indices:
        #     index = self.horizon.n_indices.index(len(self.data))
        #     self.temporal = self.horizon.scales[index]
        #     self.data.index = self.horizon.indices[self.temporal]

        # Raise error if no scale matches the length
        # else:
        #     raise ValueError(
        #         ': length of data does not match any scale index')
        #     # TODO - complete this

        # Data is a dictionary with the key being a tuple of scale indices

        self.data = self.data[self.data.columns[0]].to_dict()

        self.name = f'DSet{self._id}'

    @property
    def value(self) -> dict:
        """Returns a dictionary of data
        """
        return self.data

    def __lt__(self, other):
        if isinstance(other, (int, float)) and is_(self.bound, Bound.UPPER):
            return False
        elif isinstance(other, DataSet) and is_(other.bound, Bound.LOWER):
            return False
        else:
            return True

    def __gt__(self, other):
        if isinstance(other, (int, float)) and is_(self.bound, Bound.UPPER):
            return True
        elif isinstance(other, DataSet) and is_(other.bound, Bound.LOWER):
            return True
        else:
            return False
