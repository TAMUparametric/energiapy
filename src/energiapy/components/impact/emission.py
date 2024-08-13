from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .._base._defined import _Impact

if TYPE_CHECKING:
    from ..._core._aliases._is_input import IsExactInput


@dataclass
class Emission(_Impact):
    """Emission derived from:
    Resource Consume and Discharge
    Material Use
    Operation Capacity
    """

    emit: IsExactInput = field(default=None)

    def __post_init__(self):
        _Impact.__post_init__(self)

    @staticmethod
    def collection():
        """The collection in scenario"""
        return 'emissions'