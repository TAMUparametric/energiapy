"""For unbounded parameters
"""
from dataclasses import dataclass
from .type.special import SpecialParameter
from .data import Data
from pandas import DataFrame


@dataclass(frozen=True)
class Unbound:
    """A really big number
    Unlike the money in my bank account
    """
    name: str
    greater: bool
    special = SpecialParameter.UNBOUND

    def __gt__(self, other):
        if isinstance(other, (int, float, Data, DataFrame, dict)):
            # BigM is always greater than any number
            return self.greater
        if isinstance(other, Unbound):
            if other.greater is False:
                return self.greater
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, (int, float, Data, DataFrame, dict)):
            # BigM is always greater than any number
            return not self.greater
        if isinstance(other, Unbound):
            if other.greater is False:
                return not self.greater
        return NotImplemented

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, Unbound):
            return self.name == other.name
        return NotImplemented


BigM = Unbound(name='M', greater=True)
smallm = Unbound(name='m', greater=False)
