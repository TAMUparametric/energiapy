"""Scale is a bespoke discretization of the planning horizon (Horizon) of the problem.
"""

from dataclasses import dataclass

from .._base._discr import _Discr
from .period import Period


@dataclass
class Scale(_Discr):
    """
    A single temporal scale of the planning horizon (Horizon).

    Generated based on the discretization of the planning horizon.

    Attributes:
        index(list[tuple]): index as a list of tuples
        n_index(int): number of indices, generated post-initialization.
    """

    def __post_init__(self):
        _Discr.__post_init__(self)
        self.periods = None

    def pos(self, index: tuple) -> int:
        """Returns position of index"""
        return self.index.index(index)

    def idx(self, position: tuple):
        """Pops index"""
        return self.index[position]

    def rng(self, lb: int | tuple, ub: int | tuple):
        """Returns range from postion/index"""
        if isinstance(lb, int):
            return self.index[lb:ub]

        if isinstance(lb, tuple):
            return self.index[self.pos(lb) : self.pos(ub)]

    def periodize(self):
        """Generates periods"""
        self.periods = [Period(scale=self, period=i) for i in self.index]

    def __len__(self):
        return len(self.index)
