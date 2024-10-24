"""Keeps a track of what tasks have been defined at what indices
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ...core._handy._dunders import _Dunders
from ...core.isalias.cmps.iscmp import IsDct, IsDsp
from ...core.nirop.errors import CacodcarError
from ...elements.index import Idx

if TYPE_CHECKING:
    from .taskmaster import Chanakya
    from ..system import System


@dataclass
class ChitraGupta(_Dunders):
    """Keeps a track of what elements are defined at what indices

    Attributes:
        name (str): name, takes from the name of the Scenario
        taskmaster: Chanakya

    """

    name: str = field(default=None)
    system: System = field(default=None)
    taskmaster: Chanakya = field(default=None)

    def __post_init__(self):
        self.name = f'Registrar|{self.name}|'
        self.indices: list[Idx] = []


    def fish(self, disp: dict):
        """Fishes out an Idx declared at a particular Disposition

        Args:
            attr (str): attribute
            disposition (dict): Disposition of the Idx as a dictionary
        """
        disposition: IsDsp = tuple([v for v in disp.values() if v])
        catch: list[Idx] = [i for i in self.indices if i.disposition == disp]

        # Only one should be found, if more than one is found, it is an error
        if len(catch) > 1:
            raise CacodcarError(
                f'More than one Idx found at {disposition} in {self.name}'
            )

        if len(catch) == 1:
            index: Idx = catch[0]

        if len(catch) == 0:
            index = Idx(**disp)
            # register the index, and return a fresh Idx or found Idx
            self.indices.append(index)
        return index

    def register(self, cns: str, index: Idx):
        """Register that a Variable or Parameter has been declared at a particular Idx

        Args:
            attr (str) : cns
            index (Idx): index
        """

        indices: list[Idx] = getattr(self, cns)

        if index in indices:
            raise CacodcarError(f'{cns} already has {index} in {self.name}')

        else:
            setattr(self, cns, indices.append(index))

    def inputs(self):
        """Returns Inputs"""
        return self.taskmaster.inputs()


# @dataclass
# class ChitraGupta(_Dunders):
#     """Keeps a track of what elements are defined at what indices

#     Attributes:
#         name (str): name, takes from the name of the Scenario
#         taskmaster: Chanakya

#     """

#     name: str = field(default=None)
#     taskmaster: Chanakya = field(default=None)

#     def __post_init__(self):
#         self.name = f'Registrar|{self.name}|'

#         # make a list to store all the indices at which the task is declared
#         for attr in self.taskmaster.inputs():
#             setattr(self, attr, [])

#     def fish(self, attr: str, disposition: dict):
#         """Fishes out an Idx declared at a particular Disposition

#         Args:
#             attr (str): attribute
#             disposition (dict): Disposition of the Idx as a dictionary
#         """
#         disp: IsDsp = tuple([v for v in disposition.values() if v])
#         catch: list[Idx] = [i for i in self.indices() if i.disposition == disp]

#         # Only one should be found, if more than one is found, it is an error
#         if len(catch) > 1:
#             raise CacodcarError(
#                 f'More than one Idx found at {disposition} in {self.name}'
#             )

#         if len(catch) == 1:
#             index: Idx = catch[0]

#         if len(catch) == 0:
#             index = Idx(**disposition)
#         # register the index, and return a fresh Idx or found Idx
#         self.register(attr, index)
#         return index

#     def register(self, cns: str, index: Idx):
#         """Register that a Variable or Parameter has been declared at a particular Idx

#         Args:
#             attr (str) : cns
#             index (Idx): index
#         """

#         indices: list[Idx] = getattr(self, cns)

#         if index in indices:
#             raise CacodcarError(f'{cns} already has {index} in {self.name}')

#         else:
#             setattr(self, cns, indices.append(index))

#     def indices(self) -> list[Idx]:
#         """All indices declared

#         Args:
#             attr (str): attribute
#         """
#         return sum([getattr(self, attr) for attr in self.inputs()], [])

#     def inputs(self):
#         """Returns Inputs"""
#         return self.taskmaster.inputs()