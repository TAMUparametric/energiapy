"""There are user defined components
"""

from dataclasses import dataclass, field

from ..._core._handy._collections import _Elements, _Values
from ._component import _Component


@dataclass
class _Defined(_Component, _Values, _Elements):
    """If the component is defined by user, it should inherit from this class"""

    basis: str = field(default='unit')
    citation: dict = field(default=None)
    block: str = field(default=None)
    introduce: str = field(default=None)
    retire: str = field(default=None)
    label: str = field(default=None)

    def __post_init__(self):
        _Component.__post_init__(self)
        self._consistent = False

    def eqns(self):
        """Prints all equations in the program"""
        for constraint in self.constraints:
            print(constraint.equation)
