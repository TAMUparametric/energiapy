"""energiapy.Storage - Stashes Resource to Withdraw Later
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .._base._nature import nature
from ._operational import _Operational

# import operator
# from functools import reduce


if TYPE_CHECKING:
    from ..._core._aliases._is_input import IsExactInput


@dataclass
class Storage(_Operational):
    """Storage component

    Args:
        loss: (IsExactInput, optional): Loss of resource in storage. Defaults to None.

    """

    loss: IsExactInput = field(default=None)

    def __post_init__(self):
        _Operational.__post_init__(self)

    @staticmethod
    def resourceloss():
        """Attrs that determine resource loss of the component"""
        return nature['resourceloss']

    @staticmethod
    def resourceexps():
        """Attrs that determine resource expenses of the component"""
        return []
