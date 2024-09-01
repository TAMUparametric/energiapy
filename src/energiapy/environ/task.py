"""Task, for Component attributes
"""

from dataclasses import dataclass, field

from ..core._handy._dunders import _Dunders
from ..core._handy._printers import _EasyPrint
from ..core.isalias.cmps.isdfn import IsDfn
from ..core.isalias.elms.isvar import IsVar


@dataclass
class Task(_Dunders, _EasyPrint):
    """Task
    Handles the attributes of components
    Defines strict behaviour

    Attributes:
        attr (str): attr associated with Task
        root (list[IsDfn]): list of Components where the attribute can be declared
        other (list[IsDfn]): list of Incongruent Components where the Component attribute can be declared
        var (IsVar): Task Variable
        var_i (IsVar): Incidental Task Variable
    """

    attr: str = field(default=None)
    root: list[IsDfn] = field(default_factory=list)
    other: list[IsDfn] = field(default_factory=list)
    var: IsVar = field(default=None)
    var_i: IsVar = field(default=None)

    def __post_init__(self):
        self.name = f'Task|{self.attr}|'
        # Elements associated with the attribute
        self.values = []
        self.parameters = []
        self.constraints = []
        self.variables = []
        self.indices = []
