""" energiapy.Location
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .._component import _Spatial

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..._core._aliases._is_input import IsExactInput, IsBoundInput


@dataclass
class Location(_Spatial):
    """Location where Process and Storage can reside"""

    land_cost: IsExactInput = field(default=None)
    land_avail: IsBoundInput = field(default=None)

    def __post_init__(self):
        _Spatial.__post_init__(self)

    @staticmethod
    def collection():
        """The collection in scenario"""
        return 'locations'

    @property
    def processes(self):
        return self._system.processes

    @property
    def storages(self):
        return self._system.storages
