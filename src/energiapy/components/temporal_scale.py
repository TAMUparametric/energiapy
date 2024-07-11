"""
energiapy.TemporalScale - Planning horizon of the problem. 
Also:
    classifies the problem type (design, scheduling, simultaneous)
    determines the scale type (multiscale, single scale)
"""

from dataclasses import dataclass
from itertools import product
from typing import List, Set
from warnings import warn

from ..model.type.disposition import TemporalDisp


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
    def cname(self) -> str:
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
