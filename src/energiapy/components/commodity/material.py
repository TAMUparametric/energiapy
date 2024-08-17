from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ._commodity import _Used

if TYPE_CHECKING:
    from ..._core._aliases._is_input import IsBoundInput, IsExactInput


@dataclass
class Material(_Used):

    use: IsBoundInput = field(default=None)
    cost: IsExactInput = field(default=None)
    emission: IsExactInput = field(default=None)

    def __post_init__(self):
        _Used.__post_init__(self)
