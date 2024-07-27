"""For unbounded parameters
"""
from dataclasses import dataclass

from pandas import DataFrame

from ...core.base import Dunders
from .dataset import DataSet


@dataclass(frozen=True)
class Unbound(Dunders):
    """A really big number
    Unlike the money in my bank account
    """
    name: str
    greater: bool

    def __gt__(self, other):
        if isinstance(other, (int, float, DataSet, DataFrame, dict)):
            # BigM is always greater than any number
            return self.greater
        if isinstance(other, Unbound):
            if other.greater is False:
                return self.greater
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, (int, float, DataSet, DataFrame, dict)):
            # BigM is always greater than any number
            return not self.greater
        if isinstance(other, Unbound):
            if other.greater is False:
                return not self.greater
        return NotImplemented


BigM = Unbound(name='M', greater=True)
smallm = Unbound(name='m', greater=False)
