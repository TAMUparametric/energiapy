"""Scopes define the spatiotemporal boundaris of the System
"""

from abc import ABC, abstractmethod
from itertools import product, accumulate
from dataclasses import dataclass, field
from operator import mul
from ._component import _Component


@dataclass
class _Scope(_Component, ABC):
    """These define the spatiotemporal boundaries of the System
    Components which have only one instance in the model
    Horizon and Network are the only scope components

    Attributes:
        nested: bool, optional, default True
        birth: int | list[int] | dict[str, int], optional, default 1
        birth_labels: bool, optional, default False

    """

    birth: int | list[int] | dict[str, int] = field(default=None)
    birth_labels: list[str] = field(default=None)
    nested: bool = field(default=False)

    def __post_init__(self):
        _Component.__post_init__(self)
        self.children = []
        self.discrs = 1
        # Every Scope has a root birth
        # This root birth, basiscally the horizon
        if self.birth:
            if isinstance(self.birth, int):
                # if only a number is given, then just make
                self.birth = [self.birth]

            if isinstance(self.birth, dict):
                self.birth_list = list(self.birth.values())
                # self.birth_list.insert(0, 1)
                self.birth_names = list(self.birth.keys())
                # self.birth_names.insert(0, self._root())

            elif isinstance(self.birth, list):
                self.birth_list = self.birth
                # self.birth_list.insert(0, 1)
                self.birth_names = [
                    f'{self._def_name()}{b}' for b in range(len(self.birth_list))
                ]

            else:
                raise ValueError('Partitions must be int, list or dictionary')

            if self.nested:
                self.birth_list = list(accumulate(self.birth_list, mul))

            if not self.birth_labels:
                self.birth_labels = [None for _ in range(self.n_births)]

        else:
            self.birth_list, self.birth_names = [], []

    @property
    def index(self):
        """Index of the Network"""
        return (self,)

    @property
    @abstractmethod
    def discretizations(self):
        """Discretizations for the births"""

    @property
    @abstractmethod
    def root(self):
        """Root birth of the Scope"""

    @staticmethod
    @abstractmethod
    def _root():
        """Name for root birth of the Scope"""

    @staticmethod
    @abstractmethod
    def _def_name():
        """Default name for the Partitions"""

    @property
    def n_births(self) -> int:
        """Returns number of births"""
        return len(self.birth_list)

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
        if self.n_births > 2:
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

        lists = [list(range(i)) for i in self.birth_list]
        if nested:
            return list(product(*lists[: position + 1]))
        else:
            return [(0, i) for i in lists[position]]
