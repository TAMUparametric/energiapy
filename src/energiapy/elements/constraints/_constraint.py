"""Task, for Component attributes
"""

from dataclasses import dataclass, field

from ...core._handy._dunders import _Dunders
from ...core._handy._printers import _EasyPrint
from ...core.isalias.cmps.iscmp import IsCmp


@dataclass
class _Constraint(_Dunders, _EasyPrint):
    """Task
    Handles the attributes of components
    Defines strict behaviour

    Attributes:
        var (IsVar): Task Variable
    """

    root: IsCmp = field(default=None)

    def __post_init__(self):
        # Elements associated with the attribute
        self.values = []
        self.parameters = []
        self.constraints = []
        self.variables = []
        self.indices = []
