"""Bound input attributes for Components
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ..core.aliases.is_input import IsBoundInput


class Bounds:
    """Bound input attributes for Components"""

    @classmethod
    def bounds(cls):
        """Bounds across the Scenario"""
        return fields(cls)


@dataclass
class PlyBounds(Bounds):
    """Bounds for Players"""

    has: IsBoundInput = field(default=None)
    needs: IsBoundInput = field(default=None)


@dataclass
class CshBounds(Bounds):
    """Bounds for Cash"""

    spend: IsBoundInput = field(default=None)
    earn: IsBoundInput = field(default=None)


@dataclass
class EmnBounds(Bounds):
    """Bounds for Emission"""

    emit: IsBoundInput = field(default=None)


@dataclass
class UsedBounds(Bounds):
    """Bounds for Land and Material (Used)"""

    use: IsBoundInput = field(default=None)


@dataclass
class ResLocBounds(Bounds):
    """Bounds for Resources at Locations"""

    buy: IsBoundInput = field(default=None)
    sell: IsBoundInput = field(default=None)


@dataclass
class ResLnkBounds(Bounds):
    """Bounds for Resources at Linkages"""

    ship: IsBoundInput = field(default=None)


@dataclass
class ResBounds(ResLocBounds, ResLnkBounds):
    """Bounds for Resources"""


@dataclass
class OpnBounds(Bounds):
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
