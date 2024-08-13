"""For unbounded parameters
"""

from dataclasses import dataclass, field

from ._data import _Data
from .approach import Certainty
from .bounds import VarBnd
from .constant import Constant


@dataclass
class M(_Data):
    """
    If big is True:
        A really big number like the weight on my shoulders
    If big is False:
        really small number like the money in my bank account

    The magic methods allow sorting
    """

    big: bool = field(default=True)

    def __post_init__(self):
        _Data.__post_init__(self)

        self._certainty, self._approach, self._varbound = (
            Certainty.CERTAIN,
            None,
            VarBnd.FREE,
        )

        if self.big:
            self.name = f'M{self.name}'

        else:
            self.name = f'm{self.name}'

    @property
    def value(self):
        """Returns a str"""
        if self.big:
            return 'M'
        else:
            return 'm'

    @staticmethod
    def collection():
        """reports what collection the component belongs to"""
        return 'ms'

    @staticmethod
    def _id():
        """ID to add to name"""
        return ''

    def __gt__(self, other):
        if isinstance(other, (int, float, Constant)):
            # BigM is always greater than any number
            return getattr(self, 'big')
        if isinstance(other, M):
            if other.big is False:
                return getattr(self, 'big')
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, (int, float, Constant)):
            # BigM is always big than any number
            return not getattr(self, 'big')
        if isinstance(other, M):
            if other.big is False:
                return not getattr(self, 'big')
        return NotImplemented


BigM = M()
smallm = M(big=False)
