"""There are user defined components
"""

from dataclasses import dataclass, field

from ..._core._handy._collections import _Elms, _Vlus
from ..._core._handy._printers import _Print
from ._component import _Component


@dataclass
class _Defined(_Component, _Vlus, _Elms, _Print):
    """If the component is defined by user, it should inherit from this class

    Attributes:
        basis (str): basis of the component
        citation (dict): citation of the component
        block (str): block of the component
        introduce (str): index in scale when the component is introduced
        retire (str): index in scale when the component is retired
        label (str): label of the component
    """

    basis: str = field(default='unit')
    citation: dict = field(default=None)
    block: str = field(default=None)
    introduce: str = field(default=None)
    retire: str = field(default=None)
    label: str = field(default=None)

    def __post_init__(self):
        _Component.__post_init__(self)
        # flag to see if the inputs have been made consistent
        self._consistent = False

    def eqns(self):
        """Prints all equations in the ProgramBlock"""
        for constraint in self.constraints:
            yield constraint.equation
