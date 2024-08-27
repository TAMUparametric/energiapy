"""Constraint to calculate Variable. There is usually a parent Variable associated"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..indices.bounds import VarBnd
from ._constraint import _Constraint

if TYPE_CHECKING:
    from ..core.aliases.is_element import IsParameter, IsVariable


@dataclass
class Calculate(_Constraint):
    """Calculates; expenses, emissions, etc."""

    varbnd: VarBnd = field(default=None)
    parent: IsVariable = field(default=None)
    parameter: IsParameter = field(default=None)

    def __post_init__(self):
        _Constraint.__post_init__(self)

        # calculations always have an equality sign
        self.birth_equation(eq='==', par=self.parameter, prn=self.parent)
