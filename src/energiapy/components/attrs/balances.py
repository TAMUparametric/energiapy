"""Balance input attributes for Components
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.aliases.isinp import IsBalInput, IsConvInput


@dataclass
class ProBalance:
    """Balances for Players"""

    conversion: IsConvInput = field(default=None)


@dataclass
class StgBalance:
    """Balances for Storage"""

    inventory: IsBalInput = field(default=None)


@dataclass
class TrnBalance:
    """Balances for Transit"""

    freight: IsBalInput = field(default=None)
