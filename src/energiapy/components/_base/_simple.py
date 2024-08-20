"""If the Component is simple, it should inherit from this class"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ._consistent import _ConsistentBnd
from ._defined import _Defined


@dataclass
class _Simple(_Defined, _ConsistentBnd, ABC):
    """Simple Components inherit from this class
    They only have bounds
    These are Cash, Player, Emission, for now
    Again, do not let me tell you how to live your life
    Make more Simple Components if you feel the need
    More power to you
    """

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

        # update flag, the inputs have been made consistent
        self._consistent = True
