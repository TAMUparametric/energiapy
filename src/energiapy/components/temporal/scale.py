"""
energiapy.Scale - A bespoke discretization of the planning horizon (Horizon) of the problem. 
"""

from dataclasses import dataclass, field
from typing import List

from ...core.inits.common import CmpCommon


@dataclass
class Scale(CmpCommon):
    """
    A single temporal scale of the planning horizon (Horizon).

    Inputs:
        name(str): name. 
        index(List[tuple]): index as a list of tuples
        n_index(int): number of indices, generated post-initialization.
    """
    name: str = field(default='t0')
    index: List[tuple] = field(default_factory=list)

    @property
    def n_index(self) -> int:
        """Returns number of indices"""
        return len(self.index)
