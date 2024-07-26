"""
energiapy.TemporalScale - A bespoke discretization of the planning horizon (Horizon) of the problem. 
"""

from dataclasses import dataclass
from typing import List

from .component import ClassName, Dunders, Magics


@dataclass
class TemporalScale(Dunders, Magics, ClassName):
    """
    A single temporal scale of the planning horizon (Horizon).

    Input:
        name(str): name. 
        index(List[tuple]): index as a list of tuples
        n_index(int): number of indices, generated post-initialization.
    """
    name: str
    index: List[tuple]

    @property
    def n_index(self) -> int:
        """Returns number of indices"""
        return len(self.index)
