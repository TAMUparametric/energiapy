"""Pre-set Parameters"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..components.commodities.resource import _Commodity
from ..components.operation._operation import _Operation
from ..components.operation.storage import Stored

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

    model.Instruction(
        name="invcapex",
        kind=Stored,
        deciding="invcapacity",
        depending="spend",
        default="money",
        label="Capital Expenditure (Storage)",
    )

    model.Instruction(
        name="inventory_cost",
        kind=Stored,
        deciding="inventory",
        depending="spend",
        default="money",
        label="Inventory Cost (Storage)",
    )


def costing_commodity(model: Model):
    """Sets costing parameters for resources"""

    model.Instruction(
        name="price",
        kind=_Commodity,
        deciding="consume",
        depending="spend",
        default="money",
        label="Resource Price",
    )
