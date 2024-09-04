"""Scopes define the spatiotemporal boundaris of the System
"""

from abc import ABC, abstractmethod
from itertools import product
from dataclasses import dataclass, field

from ._component import _Component


@dataclass
class _Scope(_Component, ABC):
    """These define the spatiotemporal boundaries of the System
    Components which have only one instance in the model
    Horizon and Network are the only scope components
    """

    nested: bool = field(default=True)
    birth: int | list[int] | dict[str, int] = field(default=1)
    birth_labels: bool = field(default=False)

    def __post_init__(self):
        _Component.__post_init__(self)
        # Every Scope has a root partition
        # This root partition, basiscally the horizon
        if isinstance(self.birth, int):
            # if only a number is given, then just make
            self.birth = [self.birth]

        if isinstance(self.birth, dict):
            self._partition_list = list(self.birth.values())
            self._partition_list.insert(0, 1)
            self.name_partitions = list(self.birth.keys())
            self.name_partitions.insert(0, self._root())

        elif isinstance(self.birth, list):
            self._partition_list = self.birth
            self._partition_list.insert(0, 1)
            self.name_partitions = [
                f'{self._def_name()}{p}' for p in range(len(self._partition_list))
            ]

        else:
            raise ValueError('Partitions must be int, list or dictionary')

    @property
    @abstractmethod
    def discretizations(self):
        """Discretizations for the partitions"""

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
    def n_partitions(self) -> int:
        """Returns number of partitions"""
        return len(self._partition_list)

    @property
    def indices(self):
        """Dictionary of indices"""
        return {i: i.index for i in self.discretizations}

    @property
    def n_indices(self):
        """list of number of indices"""
        return [len(i) for i in self.discretizations]

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
        """makes an index for Discretization of the Scope
        Args:
            position: int
            nested: bool, optional, default True

        """

        lists = [list(range(i)) for i in self._partition_list]
        if nested:
            return list(product(*lists[: position + 1]))
        else:
            return [(0, i) for i in lists[position]]
