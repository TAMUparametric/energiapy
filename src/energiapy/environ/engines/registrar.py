"""Keeps a track of what tasks have been defined at what indices
"""

from dataclasses import dataclass, field

from .taskmaster import Chanakya
from ...core._handy._dunders import _Dunders
from ...core.nirop.errors import CacodcarError
from ...elements.disposition.index import Index
from ...environ.tasks.bound import Bound
from ...environ.tasks.boundbound import BoundBound
from ...environ.tasks.calculation import Calculation


@dataclass
class ChitraGupta(_Dunders):
    """Keeps a track of what elements are defined at what indices

    Attributes:
        name (str): name, takes from the name of the Scenario
        taskmaster: Chanakya

    """

    name: str = field(default=None)
    taskmaster: Chanakya = field(default=None)

    def __post_init__(self):
        self.name = f'Registrar|{self.name}|'

        # make a list to store all the indices at which the task is declared
        for attr in self.taskmaster.inputs():
            setattr(self, attr, [])

    def register(self, task: Bound | BoundBound | Calculation, index: Index):
        """Register that a Variable or Parameter has been declared at a particular Index

        Args:
            task (Bound | BoundBound | Calculation): task
            index (Index): index
        """

        task_attr = getattr(self, task.attr)

        if index in task_attr:
            raise CacodcarError(f'{task} already has {index} in {self.name}')

        else:
            setattr(self, task.attr, task_attr + [index])
