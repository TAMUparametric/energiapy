"""Storage balance"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..._core._handy._dunders import _Reprs
from ...components.commodity.resource import ResourceStr

if TYPE_CHECKING:
    from ..._core._aliases._is_component import IsStorage
    from ..._core._aliases._is_input import IsConvInput


@dataclass
class Store(_Reprs):

    store: IsConvInput = field(default=None)
    operation: IsStorage = field(default=None)

    def __post_init__(self):

        if isinstance(self.store, dict):
            self.base = list(self.store)[0]
        else:
            self.base = self.store

        self.resourcestore = ResourceStr(capacity=self.operation.capacity)
