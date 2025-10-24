"""Pre-set Parameters"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..components.commodities.resource import Commodity
from ..components.operations.operation import Operation
from ..components.operations.storage import Stored

if TYPE_CHECKING:
    from ..represent.model import Model


def costing_operation(model: Model):
    """Sets costing parameters for operations"""

    model.Instruction(
        name="capex",
        kind=Operation,
        deciding="capacity",
        depending="spend",
        default="money",
        label="Capital Expenditure",
    )
    model.Instruction(
        name="opex",
        kind=Operation,
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
        kind=Commodity,
        deciding="consume",
        depending="spend",
        default="money",
        label="Resource Price",
    )
