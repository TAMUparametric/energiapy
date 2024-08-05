"""
energiapy.Scale - A bespoke discretization of the planning horizon (Horizon) of the problem.
"""

from dataclasses import dataclass, field
from typing import List, Union

from .._initialize._component import _ScopeComponent


@dataclass
class Scale(_ScopeComponent):
    """
    A single temporal scale of the planning horizon (Horizon).

    Inputs:
        index(List[tuple]): index as a list of tuples
        n_index(int): number of indices, generated post-initialization.
    """

    index: List[tuple] = field(default_factory=list)

    def __post_init__(self):
        _ScopeComponent.__post_init__(self)

    def pos(self, index: tuple) -> int:
        """Returns position of index"""
        return self.index.index(index)

    def idx(self, position: tuple):
        """Pops index"""
        return self.index[position]

    def rng(self, lb: Union[int, tuple], ub: Union[int, tuple]):
        """Returns range from postion/index"""
        if isinstance(lb, int):
            return [self.idx(i) for i in self.index[lb:ub]]

        if isinstance(lb, tuple):
            return self.index[self.pos(lb) : self.pos(ub)]

    @property
    def n_index(self) -> int:
        """Returns number of indices"""
        return len(self.index)

    @property
    def collection(self) -> str:
        """The collection in scenario"""
        return 'scales'