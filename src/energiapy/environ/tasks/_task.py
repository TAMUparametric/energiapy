"""Task, for Component attributes
"""

from dataclasses import dataclass, field

from ...core._handy._dunders import _Dunders
from ...core._handy._printers import _EasyPrint
from ...core.isalias.cmps.iscmp import IsCmp


@dataclass
class _Task(_Dunders, _EasyPrint):
    """Task
    Handles the attributes of components
    Defines strict behaviour

    Attributes:
        var (IsVar): Task Variable
    """

    name: str = field(default=None)
    root: IsCmp = field(default=None)
    varsym: str = field(default=None)
    prmsym: str = field(default=None)

    def __post_init__(self):
        # Elements associated with the attribute
        self.values = []
        self.parameters = []
        self.constraints = []
        self.variables = []
        self.indices = []

