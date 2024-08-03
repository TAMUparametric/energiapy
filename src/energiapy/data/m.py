"""For unbounded parameters
"""
from dataclasses import dataclass, field

from .bounds import Certainty, VarBnd
from .dataset import DataSet
from .theta import Theta
from .value import Value


@dataclass
class M(Value):
    """
    If big is True: 
        A really big number like the weight on my shoulders
    If big is False: 
        really small number like the money in my bank account

    The magic methods allow sorting
    """
    big: bool = field(default=True)

    def __post_init__(self):
        if self.big:
            self.name = 'M'
        else:
            self.name = 'm'

        self._certainty, self._approach, self._varbound = Certainty.CERTAIN, None, VarBnd.FREE

    # TODO - fix add Number
    def __gt__(self, other):
        if isinstance(other, (int, float, Theta, DataSet)):
            # BigM is always greater than any number
            return getattr(self, 'big')
        if isinstance(other, M):
            if other.big is False:
                return getattr(self, 'big')
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, (int, float, Theta, DataSet)):
            # BigM is always big than any number
            return not getattr(self, 'big')
        if isinstance(other, M):
            if other.big is False:
                return not getattr(self, 'big')
        return NotImplemented


BigM = M()
smallm = M(big=False)
