"""Aspect describes the behavior of a component using model elements 
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Union


from .._core._handy._dunders import _Dunders

if TYPE_CHECKING:
    from .._core._aliases._is_task import IsTask
    from .._core._aliases._is_element import IsVariable
    from .._core._aliases._is_component import (
        IsComponent,
        IsCommodity,
        IsOperational,
        IsSpatial,
    )


@dataclass
class _Task(_Dunders):
    """Component Task"""

    dependent: IsTask = field(default=None)
    variable: IsVariable = field(default=None)
    root: IsComponent = field(default=None)
    give: IsCommodity = field(default=None)
    take: IsCommodity = field(default=None)
    opn: Union[IsOperational, List[IsOperational]] = field(default=None)
    spt: Union[IsSpatial, List[IsSpatial]] = field(default=None)

    def __post_init__(self):

        if not self.check_consistency(
            self.root, self.give, self.take, self.opn, self.spt
        ):
            raise ValueError('Task is inconsistent')

    def check_root(self, root: IsComponent):
        """Check if the root type is correct"""
        return isinstance(root, getattr(self, 'cl_root'))

    def check_give(self, give: IsCommodity):
        """Check if the given commodity type is correct"""
        return isinstance(give, getattr(self, 'cl_give'))

    def check_take(self, take: IsCommodity):
        """Check if the taken commodity type is correct"""
        return isinstance(take, getattr(self, 'cl_take'))

    def check_opn(self, opn: IsOperational):
        """Check if the operation type is correct"""
        if isinstance(self.opn, list):
            return any(isinstance(opn, getattr(self, 'cl_opn')) for opn in self.opn)
        else:
            return isinstance(opn, getattr(self, 'cl_opn'))

    def check_spt(self, spt: IsSpatial):
        """Check if the spatial type is correct"""
        if isinstance(self.spt, list):
            return any(isinstance(spt, getattr(self, 'cl_spt')) for spt in self.spt)
        else:
            return isinstance(spt, getattr(self, 'cl_spt'))

    def check_consistency(
        self,
        root: IsComponent,
        give: IsCommodity,
        take: IsCommodity,
        opn: IsOperational,
        spt: IsSpatial,
    ):
        """Check if the root, given and taken commodities, operation, and spatial types are consistent"""
        return (
            self.check_root(root)
            and self.check_give(give)
            and self.check_take(take)
            and self.check_opn(opn)
            and self.check_spt(spt)
        )
