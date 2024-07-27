from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..type.alias import IsLoss


@dataclass(kw_only=True)
class StrLoss:
    """Resource lost during storage
    """
    store_loss: IsLoss = field(default=None)


@dataclass(kw_only=True)
class TrnLoss:
    """Resource lost during transport
    """
    transport_loss: IsLoss = field(default=None)
