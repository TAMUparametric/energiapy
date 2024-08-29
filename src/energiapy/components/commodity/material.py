"""Material used by Operations
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ._commodity import _Used

if TYPE_CHECKING:
    from ...core.aliases.is_input import IsBoundInput, IsExactInput


@dataclass
class Material(_Used):
    """Material used to set up Operations

    Attributes:
        use (IsBoundInput): bound for use at some spatiotemporal disposition
        cost (IsExactInput): cost per a unit basis at some spatiotemporal disposition
        emission (IsExactInput): emission per unit basis of use
        basis (str): basis of the component
        citation (dict): citation of the component
        block (str): block of the component
        introduce (str): index in scale when the component is introduced
        retire (str): index in scale when the component is retired
        label (str): label of the component

    """

    def __post_init__(self):
        _Used.__post_init__(self)

    @property
    def uses(self):
        """Material Uses across the Scenario"""
        return self.taskmaster.report_uses_material
