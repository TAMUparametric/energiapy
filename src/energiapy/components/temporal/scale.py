"""Scale is a bespoke discretization of the planning horizon (Horizon) of the problem.
"""

from dataclasses import dataclass

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

    periods: int

    def __post_init__(self):
        _Component.__post_init__(self)

    def __len__(self):
        return self.periods
