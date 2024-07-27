from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..aspect import Aspect

if TYPE_CHECKING:
    from ...type.alias import IsAspect, IsCommodity, IsOperation, IsSpatial

from ...type.alias import IsLimit


@dataclass
class Limit(Aspect):
    """A limit to Component behavior
    """
    commodity: IsCommodity = field(default=None)
    operation: IsOperation = field(default=None)
    spatial: IsSpatial = field(default=None)
    opn_strict: bool = False
    spt_strict: bool = False

    @property
    def _behavior(self):
        return IsLimit
