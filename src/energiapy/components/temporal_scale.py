"""
energiapy.TemporalScale - A bespoke discretization of the planning horizon (Horizon) of the problem. 
"""

from dataclasses import dataclass
from typing import List


@dataclass
class TemporalScale:
    """
    A single temporal scale of the planning horizon (Horizon).

    Attributes:
        name(str): name. 
        index(List[tuple]): index as a list of tuples
        n_index(int): number of indices, generated post-initialization.
    """
    name: str
    index: List[tuple]

    # * ---------Methods-----------------

    @staticmethod
    def cname() -> str:
        """Returns class name"""
        return 'TemporalScale'

    @property
    def n_index(self) -> int:
        """Returns number of indices"""
        return len(self.index)

    # * ---------Dunders-----------------

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
