"""If the component is simple, it should inherit from this class"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ._consistent import _ConsistentBnd
from ._defined import _Defined


@dataclass
class _Simple(_Defined, _ConsistentBnd, ABC):

    def __post_init__(self):
        _Defined.__post_init__(self)

    @staticmethod
    @abstractmethod
    def bounds():
        """Attrs that quantify the bounds of the component"""

    @classmethod
    def inputs(cls):
        """Attrs"""
        return cls.bounds()

    def make_consistent(self):
        """Makes the data inputs consistent IsSptTmpDict"""
        for attr in self.inputs():
            if getattr(self, attr) is not None:
                if attr in self.bounds():
                    self.make_bounds_consistent(attr)

        self._consistent = True
