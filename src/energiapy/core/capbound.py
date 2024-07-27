from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..type.alias import IsCapBound


@dataclass(kw_only=True)
class PrcCapBound:
    """Resource Cap Bound for Process
    """
    produce: IsCapBound = field(default=None)


@dataclass(kw_only=True)
class StrCapBound:
    """Resource Cap Bound for Storage
    """
    store: IsCapBound = field(default=None)


@dataclass(kw_only=True)
class TrnCapBound:
    """Resource Cap Bound for Transport
    """
    transport: IsCapBound = field(default=None)


@dataclass(kw_only=True)
class RscCapBound:
    """Resource Cap Bounds
    """

    def __post_init__(self):
        for i in ['produce', 'store', 'transport']:
            setattr(self, i, None)
