"""Keeps a track of what tasks have been defined at what indices
"""

from dataclasses import dataclass, field

from .taskmaster import Chanakya
from ...core._handy._dunders import _Dunders
from ...core.nirop.errors import CacodcarError
from ...elements.disposition.index import Index
from ...environ.tasks.bound import Bound, BoundBound
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
        self.pbounds, self.mbounds, self.boundbounds, self.calculations = (
            {} for _ in range(4)
        )

    def register(self, task: Bound | BoundBound | Calculation, index: Index):
        """Register that a Variable or Parameter has been declared at a particular Index

        Args:
            task (Bound | BoundBound | Calculation): task
            index (Index): index
        """

        if isinstance(task, Bound):
            collection = (
                getattr(self, 'pbounds') if task.p else getattr(self, 'mbounds')
            )

        if isinstance(task, BoundBound):
            collection = getattr(self, 'boundbounds')

        if isinstance(task, Calculation):
            collection = getattr(self, 'calculations')

        if task.name in collection:

            if index in collection[task.name]:
                raise CacodcarError(f'{task} already has {index} in {self.name}')

            collection[task.name].append(index)

        else:
            collection[task.name] = [index]
