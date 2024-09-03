"""Scopes define the spatiotemporal boundaris of the System
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from ._component import _Component

from ...utils.dictionary import tupler, get_depth
from itertools import product


@dataclass
class _Scope(_Component, ABC):
    """These define the spatiotemporal boundaries of the System
    Components which have only one instance in the model
    Horizon and Network are the only scope components
    """

    nested: bool = field(default=False)
    label: str = field(default=None)

    def __post_init__(self):
        _Component.__post_init__(self)

        if isinstance(self.partitions, int):
            self.partitions = [self.partitions]

        if isinstance(self.partitions, dict):
            if get_depth(self.partitions) > 1:
                self.partitions = {i[-1]: i for i in tupler(self.partitions)}
                self.partitions[self._root] = tuple(
                    [p[0] for p in list(self.partitions) if len(p) == 1]
                )
                self._tuplered = True
            else:
                self._tuplered = False
                self._partition_list = list(self.partitions.values())
                self._partition_list.insert(0, 1)

            self.name_partitions = list(self.partitions.keys())
            self.name_partitions.insert(0, self._root())

        elif isinstance(self.partitions, list):
            self._tuplered = False
            self._partition_list = self.partitions
            self._partition_list.insert(0, 1)
            self.name_partitions = [
                f'{self._def_name()}{p}' for p in self._partition_list
            ]

        else:
            raise ValueError('Partitions must be int, list or dictionary')

    @property
    @abstractmethod
    def partitions(self):
        """Partitions to divide the Scope into"""

    @property
    @abstractmethod
    def root(self):
        """Root partition of the Scope"""

    @staticmethod
    @abstractmethod
    def _root():
        """Name for root partition of the Scope"""

    @staticmethod
    @abstractmethod
    def _def_name():
        """Default name for the Partitions"""

    @property
    @abstractmethod
    def label_partitions(self):
        """Labels for the partitions"""

    @property
    def n_partitions(self) -> int:
        """Returns number of partitions"""
        return len(self._partition_list)

    @property
    def indices(self):
        """Dictionary of indices"""
        return {i: i.index for i in self.partitions}

    @property
    def n_indices(self):
        """list of number of indices"""
        return [len(i) for i in self.partitions]

    @property
    def is_multiscale(self):
        """Returns True if problem has multiple scales"""
        # Note that the first scale is always the planning horizon
        if self.n_partitions > 2:
            return True
        else:
            return False

    @property
    def is_nested(self):
        """Returns True if problem has nested scales"""
        if self.nested:
            return True
        else:
            return False

    def make_index(self, position: int, nested: bool = True):
        """makes an index for Scale"""

        if self._tuplered:
            return self.partitions[position]
        else:
            lists = [list(range(i)) for i in self._partition_list]
            if nested:
                return list(product(*lists[: position + 1]))
            else:
                return [(0, i) for i in lists[position]]
