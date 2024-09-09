"""Keeps a track of what tasks have been defined at what indices
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ...core._handy._dunders import _Dunders
from ...core.nirop.errors import CacodcarError
from ...core.isalias.cmps.iscmp import IsDsp
from ...elements.disposition.index import Index

if TYPE_CHECKING:
    from .taskmaster import Chanakya


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

    def fish(self, attr: str, disposition: dict):
        """Fishes out an Index declared at a particular Disposition

        Args:
            attr (str): attribute
            disposition (dict): Disposition of the Index as a dictionary
        """
        disp = tuple([v for v in disposition.values() if v])
        catch = [i for i in self.indices() if i.disposition == disp]

        # Only one should be found, if more than one is found, it is an error
        if len(catch) > 1:
            raise CacodcarError(
                f'More than one Index found at {disposition} in {self.name}'
            )

        if len(catch) == 1:
            index = catch[0]

        if len(catch) == 0:
            index = Index(**disposition)
        # register the index, and return a fresh Index or found Index
        self.register(attr, index)
        return index

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
        """All indices declared

        Args:
            attr (str): attribute
        """
        return sum([getattr(self, attr) for attr in self.inputs()], [])

    def inputs(self):
        """Returns Inputs"""
        return self.taskmaster.inputs()
