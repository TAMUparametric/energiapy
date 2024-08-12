"""energiapy.Storage - Stashes Resource to Withdraw Later
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .._base._defined import _Operational

# import operator
# from functools import reduce


if TYPE_CHECKING:
    from ..._core._aliases._is_input import IsExactInput


@dataclass
class Storage(_Operational):
    loss: IsExactInput = field(default=None)

    def __post_init__(self):
        _Operational.__post_init__(self)

    @staticmethod
    def quantify():
        """The quantified data inputs to the component"""
        return ['capacity', 'operate', 'use', 'loss']

    @staticmethod
    def expenses():
        """The quantified costs of the component"""
        return ['capex', 'opex']

    @staticmethod
    def collection():
        """The collection in scenario"""
        return 'storages'


# store: Resource
#     capacity: IsLimit
#     land_use: IsLand = field(default=None)
#     material_cons: IsMatUse = field(default=None)
