"""Bound input attributes for Components
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ..core.aliases.is_input import IsBoundInput


@dataclass
class PlyBounds:
    """Bounds for Players"""

    has: IsBoundInput = field(default=None)
    needs: IsBoundInput = field(default=None)


@dataclass
class CshBounds:
    """Bounds for Cash"""

    spend: IsBoundInput = field(default=None)
    earn: IsBoundInput = field(default=None)


@dataclass
class EmnBounds:
    """Bounds for Emission"""

    emit: IsBoundInput = field(default=None)


@dataclass
class UsedBounds:
    """Bounds for Land and Material (Used)"""

    use: IsBoundInput = field(default=None)


@dataclass
class ResLocBounds:
    """Bounds for Resources at Locations"""

    buy: IsBoundInput = field(default=None)
    sell: IsBoundInput = field(default=None)


@dataclass
class ResLnkBounds:
    """Bounds for Resources at Linkages"""

    ship: IsBoundInput = field(default=None)


@dataclass
class ResBounds(ResLocBounds, ResLnkBounds):
    """Bounds for Resources"""


@dataclass
class OpnBounds:
    """Bounds for Operational Components"""

    capacity: IsBoundInput = field(default=None)


@dataclass
class ProBounds(OpnBounds):
    """Bounds for Process"""

    produce: IsBoundInput = field(default=None)


@dataclass
class StgBounds(OpnBounds):
    """Bounds for Storage"""

    store: IsBoundInput = field(default=None)
    capacity_in: IsBoundInput = field(default=None)
    capacity_out: IsBoundInput = field(default=None)


@dataclass
class TrnBounds(OpnBounds):
    """Bounds for Transit"""

    transport: IsBoundInput = field(default=None)
