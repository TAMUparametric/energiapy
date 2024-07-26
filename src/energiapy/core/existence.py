from __future__ import annotations

from dataclasses import dataclass, field

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..type.alias import IsLife


@dataclass
class Existence:
    """Existence of Operation
    """
    introduce: IsLife = field(default=None)
    retire: IsLife = field(default=None)
    lifetime: IsLife = field(default=None)
    pfail: IsLife = field(default=None)
    trl: IsLife = field(default=None)
