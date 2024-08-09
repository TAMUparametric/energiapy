"""DataSet is a deterministic data given to account for temporal variability in parameter.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from operator import is_
from typing import TYPE_CHECKING

from pandas import DataFrame

from ._approach import _Approach, _Certainty
from ._bounds import _VarBnd
# from ..core.base import Dunders
from ._value import _Value

if TYPE_CHECKING:
    from .._core._aliases._is_input import IsDataFr


@dataclass
class DataSet(_Value):
    data: IsDataFr = field(default=None)

    def __post_init__(self):
        _Value.__post_init__(self)
        # Data has to be provided as a DataFrame
        if not isinstance(self.data, DataFrame):
            raise ValueError(f'{self.name}: please provide DataFrame')

        self._certainty, self._approach, self._varbound = (
            _Certainty.UNCERTAIN,
            _Approach.DATA,
            _VarBnd.EXACT,
        )

        self.data = self.data[self.data.columns[0]].to_dict()

        self.name = f'DSet{self._id}'

    @property
    def value(self) -> dict:
        """Returns a dictionary of data"""
        return self.data

    # TODO - complete this
    def __lt__(self, other):
        if isinstance(
                other, (int, float)) and is_(
                self._varbound, _VarBnd.UPPER):
            return False
        elif isinstance(other, DataSet) and is_(other.varbound, _VarBnd.LOWER):
            return False
        else:
            return True

    def __gt__(self, other):
        if isinstance(
                other, (int, float)) and is_(
                self._varbound, _VarBnd.UPPER):
            return True
        elif isinstance(other, DataSet) and is_(other.varbound, _VarBnd.LOWER):
            return True
        else:
            return False
