"""Scale is a bespoke discretization of the planning horizon (Horizon) of the problem.
"""

from dataclasses import dataclass
from typing import Self


@dataclass
class Period:
    """
    A single temporal scale of the planning horizon (Horizon).

    Generated based on the discretization of the planning horizon.

    Attributes:
        index(list[tuple]): index as a list of tuples
        n_index(int): number of indices, generated post-initialization.
    """

    number: int

    def __len__(self):
        return self.number

    def __getitem__(self, item: int):
        return Period(item)

    def __iter__(self):
        return iter(range(self.number))

    def __reversed__(self):
        return reversed(range(self.number))

    def __contains__(self, item: int):
        return item in range(self.number)

    def __eq__(self, other: Self):
        return self.number == other.number

    def __ne__(self, other: Self):
        return self.number != other.number

    def __lt__(self, other: Self):
        return self.number < other.number
