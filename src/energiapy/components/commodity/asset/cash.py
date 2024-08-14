from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..._base._defined import _Asset
from ..._base._nature import nature

if TYPE_CHECKING:
    from ...._core._aliases._is_input import IsBoundInput


@dataclass
class Cash(_Asset):
    """Cash derived from:
    Resource Consume and Discharge
    Operation Capacity
    Process Produce
    Storage Store
    Transit Transport
    """

    spend: IsBoundInput = field(default=None)
    earn: IsBoundInput = field(default=None)

    def __post_init__(self):
        _Asset.__post_init__(self)

    @staticmethod
    def collection():
        """The collection in scenario"""
        return 'cash'

    