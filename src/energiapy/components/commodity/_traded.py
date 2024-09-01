"""Base for any Traded Component
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from .._base._defined import _Defined
from ._commodity import _Commodity


@dataclass
class _Traded(_Defined, _Commodity, ABC):
    """Applied for Land, Material and Resource"""

    def __post_init__(self):
        _Defined.__post_init__(self)
        _Commodity.__post_init__(self)

    @staticmethod
    @abstractmethod
    def inputs():
        """Input Attributes"""
