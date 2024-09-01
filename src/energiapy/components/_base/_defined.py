"""There are user defined components
"""

from dataclasses import dataclass, field

from ...core._handy._printers import _EasyPrint
from ...core._report._data import _Vlus
from ...core._report._prog import _Elms
from ._component import _Component
from ._consistent import _Consistent


@dataclass
class _Defined(_Component, _Consistent, _Vlus, _Elms, _EasyPrint):
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


@dataclass
class _Simple(_Defined):
    """Simple Components inherit from this class
    They only have bounds
    These are Cash, Player, Emission, for now
    Again, do not let me tell you how to live your life
    Make more Simple Components if you feel the need
    More power to you
    """

    def __post_init__(self):
        _Defined.__post_init__(self)
