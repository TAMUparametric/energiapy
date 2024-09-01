"""Scale is a bespoke discretization of the planning horizon (Horizon) of the problem.
"""

from dataclasses import dataclass, field

from .._base._component import _Component


@dataclass
class Scale(_Component):
    """
    A single temporal scale of the planning horizon (Horizon).

    Generated based on the discretization of the planning horizon.

    Attributes:
        index(list[tuple]): index as a list of tuples
        n_index(int): number of indices, generated post-initialization.
    """

    index: list[tuple] = field(default_factory=list)
    label: str = field(default=None)

    def __post_init__(self):
        _Component.__post_init__(self)

    def pos(self, index: tuple) -> int:
        """Returns position of index"""
        return self.index.index(index)

    def idx(self, position: tuple):
        """Pops index"""
        return self.index[position]

    def rng(self, lb: int | tuple, ub: int | tuple):
        """Returns range from postion/index"""
        if isinstance(lb, int):
            return [self.idx(i) for i in self.index[lb:ub]]

        if isinstance(lb, tuple):
            return self.index[self.pos(lb) : self.pos(ub)]

    def __len__(self):
        return len(self.index)
