from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ...core.inits.common import ElmCommon

if TYPE_CHECKING:
    from ..type.alias import IsIndex, IsValue


@dataclass
class Variable(ElmCommon):
    index: IsIndex = field(default=None)
