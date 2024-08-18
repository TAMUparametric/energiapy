"""energiapy.Storage - Stashes Resource to Withdraw Later
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ._operational import _Operational

# import operator
# from functools import reduce


if TYPE_CHECKING:
    from ..._core._aliases._is_input import IsBoundInput, IsExactInput


@dataclass
class Storage(_Operational):
    """Storage component

    Args:
        loss: (IsExactInput, optional): Loss of resource in storage. Defaults to None.

    """

    store: IsExactInput = field(default=None)
    loss: IsBoundInput = field(default=None)

    def __post_init__(self):
        _Operational.__post_init__(self)

    @property
    def _operate(self):
        """Returns attribute value that signifies operating bounds"""
        return self.store

    @staticmethod
    def resourcebnds():
        """Attrs that quantify the bounds of the Component"""
        return []

    @staticmethod
    def resourceexps():
        """Attrs that determine resource expenses of the component"""
        return []

    @staticmethod
    def resourceloss():
        """Attrs that determine resource loss of the component"""
        return ['loss']
