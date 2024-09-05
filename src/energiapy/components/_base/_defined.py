"""There are user defined components
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from ...core._handy._printers import _EasyPrint
from ...core._report._data import _Vlus
from ...core._report._prog import _Elms
from ._component import _Component
from ._consistent import _Consistent


@dataclass
class _Defined(_Component, _Consistent, _Vlus, _Elms, _EasyPrint, ABC):
    """If the component is defined by user, it should inherit from this class

    Attributes:
        basis (str): basis of the component
        citation (dict): citation of the component
        block (str): block of the component
        introduce (str): index in scale when the component is introduced
        retire (str): index in scale when the component is retired
        label (str): label of the component
    """

    basis: str = field(default=None)
    citation: dict = field(default=None)
    block: str = field(default=None)
    introduce: str = field(default=None)
    retire: str = field(default=None)

    def __post_init__(self):
        _Component.__post_init__(self)
        # This flag is used to check if the Defined Component has been located
        # i.e., assigned to a Location or Linkage
        self._located = False

    @staticmethod
    @abstractmethod
    def inputs():
        """Input attributes"""
