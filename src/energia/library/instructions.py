"""Pre-set Parameters"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..components.operation._operation import _Operation

if TYPE_CHECKING:
    from ..represent.model import Model


def costing_operation(model: Model):
    """Sets costing parameters for operations"""

    model.Instruction(
        name="capex",
        kind=_Operation,
        deciding="capacity",
        depending="spend",
        default="money",
        label="Capital Expenditure",
    )
    model.Instruction(
        name="opex",
        kind=_Operation,
        deciding="operate",
        depending="spend",
        default="money",
        label="Operational Expenditure",
    )
