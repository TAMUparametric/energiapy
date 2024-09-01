"""Report for collection attributes 
"""

from dataclasses import dataclass, field

from ..core._handy._dunders import _Dunders
from ..core._handy._printers import _EasyPrint
from .task import Task


@dataclass
class Report(_Dunders, _EasyPrint):
    """Report is a collection of Tasks

    Taskibutes:
        name (str): The name of the attribute collection
        tasks (list[Task]): list of TaskBlocks that the collection consists of
    """

    name: str = field(default=None)
    tasks: list[Task] = field(default_factory=list)

    def __post_init__(self):
        self.name = f'Report|{self.name}|'
        # Report associated with the attribute
        self.values = sum([attr.values for attr in self.tasks], [])
        self.parameters = sum([attr.parameters for attr in self.tasks], [])
        self.indices = sum([attr.indices for attr in self.tasks], [])
        self.constraints = sum([attr.constraints for attr in self.tasks], [])
        self.variables = sum([attr.variables for attr in self.tasks], [])
