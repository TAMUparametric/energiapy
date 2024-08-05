"""DataSet is a deterministic data given to account for temporal variability in parameter.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from operator import is_
from typing import TYPE_CHECKING

from pandas import DataFrame
from sklearn.preprocessing import MinMaxScaler, StandardScaler

from .bounds import Approach, Certainty, VarBnd
# from ..core.base import Dunders
from .value import Value

if TYPE_CHECKING:
    from ..components.horizon import Horizon
    from ..type.alias import (IsAspect, IsComponent, IsData, IsDeclaredAt,
                              IsIndex)


@dataclass
class DataSet(Value):
    data: IsData = field(default=None)

    def __post_init__(self):
        Value.__post_init__(self)
        # Data has to be provided as a DataFrame
        if not isinstance(self.data, DataFrame):
            raise ValueError(f'{self.name}: please provide DataFrame')

        self._certainty, self._approach, self._varbound = (
            Certainty.UNCERTAIN,
            Approach.DATA,
            VarBnd.EXACT,
        )

        self.data = self.data[self.data.columns[0]].to_dict()

        self.name = f'DSet{self._id}'

    @property
    def value(self) -> dict:
        """Returns a dictionary of data"""
        return self.data

    # TODO - complete this
    def __lt__(self, other):
        if isinstance(other, (int, float)) and is_(self._varbound, VarBnd.UPPER):
            return False
        elif isinstance(other, DataSet) and is_(other.varbound, VarBnd.LOWER):
            return False
        else:
            return True

    def __gt__(self, other):
        if isinstance(other, (int, float)) and is_(self._varbound, VarBnd.UPPER):
            return True
        elif isinstance(other, DataSet) and is_(other.varbound, VarBnd.LOWER):
            return True
        else:
            return False
