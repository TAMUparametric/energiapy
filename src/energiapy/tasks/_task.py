"""Aspect describes the behavior of a component using model elements 
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Union, TypeVar

from src.energiapy import data

from .._core._aliases._is_component import IsLocation


from .._core._handy._dunders import _Dunders

if TYPE_CHECKING:
    from .._core._aliases._is_task import IsTask
    from .._core._aliases._is_element import IsVariable
    from .._core._aliases._is_component import (
        IsComponent,
        IsCommodity,
        IsOperational,
        IsSpatial,
        IsPlayer,
        IsNetwork,
    )


@dataclass
class _Task(_Dunders):
    """Component Task"""

    specific: IsComponent = field(default=None)
    dependent: IsTask = field(default=None)
    variable: IsVariable = field(default=None)
    between: Union[IsPlayer, IsLocation] = field(default=None)
    at: IsComponent = field(default=None)
    give: IsCommodity = field(default=None)
    take: IsCommodity = field(default=None)
    opn: Union[IsOperational, List[IsOperational]] = field(default=None)
    spt: Union[IsSpatial, List[IsSpatial]] = field(default=None)

    def __post_init__(self):

        if not self.check_types(
            self.between, self.at, self.give, self.take, self.opn, self.spt
        ):
            raise ValueError('Task types are not correct')

    def check_between(self, between: Union[IsPlayer, IsLocation]):
        """Check if the between type is correct"""
        return isinstance(between, getattr(self, '_between'))

    def check_at(self, at: IsComponent):
        """Check if the at type is correct"""
        return isinstance(at, getattr(self, '_at'))

    def check_give(self, give: IsCommodity):
        """Check if the given commodity type is correct"""
        return isinstance(give, getattr(self, '_give'))

    def check_take(self, take: IsCommodity):
        """Check if the taken commodity type is correct"""
        return isinstance(take, getattr(self, '_take'))

    def check_opn(self, opn: Union[IsOperational, List[IsOperational]]):
        """Check if the operation type is correct"""
        if isinstance(self.opn, list):
            return any(isinstance(opn, getattr(self, '_opn')) for opn in self.opn)
        else:
            return isinstance(opn, getattr(self, '_opn'))

    def check_spt(self, spt: Union[IsSpatial, List[IsSpatial]]):
        """Check if the spatial type is correct"""
        if isinstance(self.spt, list):
            return any(isinstance(spt, getattr(self, '_spt')) for spt in self.spt)
        else:
            return isinstance(spt, getattr(self, '_spt'))

    def check_types(
        self,
        between: Union[IsPlayer, IsLocation],
        at: IsComponent,
        give: IsCommodity,
        take: IsCommodity,
        opn: Union[IsOperational, List[IsOperational]],
        spt: Union[IsSpatial, List[IsSpatial]],
    ):
        """Check if the at, given and taken commodities, operation, and spatial types are consistent"""
        return (
            self.check_between(between)
            and self.check_at(at)
            and self.check_give(give)
            and self.check_take(take)
            and self.check_opn(opn)
            and self.check_spt(spt)
        )


# Comp = TypeVar('Comp')


# class _TaskMaster:
#     """TaskMaster class"""

#     def add(
#         self,
#         name: str,
#         at: Comp,
#         also: Comp,
#         between: Comp,
#         optl_spt: Comp,
#         give: Comp,
#         take: Comp,
#     ):
#         """Add a task to the TaskMaster"""
#         setattr(
#             self,
#             name,
#             {
#                 'at': at,
#                 'between': between,
#                 'optl_spt': optl_spt,
#                 'give': give,
#                 'take': take,
#             },
#         )

# taskmaster = _TaskMaster()

# add_tasks = {
#     'trade': {'at': Resource, 'also': Process, 'between': Player, 'optl_spt': [Network, Location], 'give': Resource, 'take': Resource},
#     'transact': {'at': Resource, 'also': Process, 'between': Player, 'optl_spt': [Network, Location], 'give': Cash, 'take': Resource},
#     'ship': {'at': Resource, 'also': Transit, 'between': Location, 'optl_spt': [Network, Linkage], 'give': Resource, 'take': Resource},
#     'capacitate' : {'at': [Process, Storage, Transit], 'also': None, 'between': None, 'optl_spt': [Network, Location, Linkage]},

# }


# taskmaster.add(name= 'trade', at= Resource, also =Process, between= Player, optl_spt= [Network, Location], give= Resource, take= Resource)
# taskmaster.add(name = 'transact', at = Resource, also = Process, between = Player, optl_spt = [Network, Location], give = Cash, take = Resource)
# taskmaster.add(name = 'ship', at = Resource, also = Transit, between = Location, optl_spt = [Network, Linkage], give = Resource, take = Resource)
# taskmaster.add()
