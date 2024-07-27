from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..type.alias import IsDetail


@dataclass
class CompDetail:
    """For bookeeping purposes, this class is used to keep track of details
    """
    basis: IsDetail = field(default=None)
    block: IsDetail = field(default=None)
    label: IsDetail = field(default=None)
    citation: IsDetail = field(default=None)
