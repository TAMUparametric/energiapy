"""Keeps a track of what tasks have been defined at what indices
"""

from dataclasses import dataclass, field

from .taskmaster import Chanakya
from ...core._handy._dunders import _Dunders
from ...core.nirop.errors import CacodcarError
from ...elements.disposition.index import Index


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

    def fish(self, index: Index):
        """Fish the tasks declared at a particular Index

        Args:
            index (Index): index
        """
        if index in self.indices():
            return self.indices()[self.indices().index(index)]
        else:
            return None

    def register(self, attr: str, index: Index):
        """Register that a Variable or Parameter has been declared at a particular Index

        Args:
            attr (str) : task
            index (Index): index
        """

        task_attr = getattr(self, attr)

        if index in task_attr:
            raise CacodcarError(f'{attr} already has {index} in {self.name}')

        else:
            setattr(self, attr, task_attr + [index])

    def indices(self):
        """_summary_

        Args:
            attr (str): _description_
        """
        return sum([getattr(self, attr) for attr in self.inputs()], [])

    def inputs(self):
        """Returns Inputs"""
        return self.taskmaster.inputs()
