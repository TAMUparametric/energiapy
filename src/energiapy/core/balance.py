"""To describe use of material
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..funcs.input.conversion import conversioner

if TYPE_CHECKING:
    from ..type.alias import IsConv, IsMatUse


@dataclass
class OpnMatUse:
    """Amount of Material used by Operation
    per unit basis
    """
    material_use: IsMatUse = field(default=None)

    def __post_init__(self):
        self.materials = []


@dataclass
class PrcRscConv:
    """Balance of Resource for Process
    """
    conversion: IsConv = field(default=None)

    def make_conversion(self):
        """Makes Conversion for Process
        """
        conversioner(process=self)
