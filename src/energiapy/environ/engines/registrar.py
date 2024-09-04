"""Keeps a track of what tasks have been defined at what indices
"""

from dataclasses import dataclass, field

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
        rulebook: Bhaskara = field(default_factory=rulebook)

    """

    name: str = field(default=None)

    def __post_init__(self):

        self.name = f'Registrar|{self.name}|'
        self.pbounds, self.mbounds, self.boundbounds, self.calculations = (
            [] for _ in range(4)
        )

    def register(self, task: Bound | BoundBound | Calculation, index: Index):
        """Register that a Variable or Parameter has been declared at a particular Index

        Args:
            elm (IsElm): Element to update
            index (Index): with this Index
        """

        if isinstance(task, Bound):
            collection = 'pbounds' if task.p else 'mbounds'

        if isinstance(task, BoundBound):
            collection = 'boundbounds'

        if isinstance(task, Calculation):
            collection = 'calculations'

        if task in getattr(self, collection):
            raise CacodcarError(f'{task} already has {index} in {self.name}')

        getattr(self, collection).append(index)
