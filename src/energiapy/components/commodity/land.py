from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..component import Commodity

if TYPE_CHECKING:
    from ...type.alias import IsDepreciated, IsLimit


@dataclass
class Land(Commodity):
    pass
