"""There are user defined components
"""

from dataclasses import dataclass, field

from ...core._handy._printers import _EasyPrint
from ._component import _Component
from ._consistent import _Consistent
from ...environ.datum import Datum


@dataclass
class _Defined(_Component, _Consistent, _EasyPrint):
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
    label: str = field(default=None)

    def __post_init__(self):
        _Component.__post_init__(self)
        # This flag is used to check if the Defined Component has been located
        # i.e., assigned to a Location or Linkage
        self._located = False

    def datumize(self):
        """makes Datums out of available data"""
        # if input attr has value, make it a Datum
        for i in self.inputs():
            if getattr(self, i, False):
                setattr(self, i, Datum(attr=i, data=getattr(self, i), component=self))
