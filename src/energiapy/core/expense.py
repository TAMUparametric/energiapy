from __future__ import annotations

from dataclasses import dataclass, field

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..type.alias import IsCashFlow


@dataclass
class ResExpense:
    """Cash flow of Commodities
    """
    sell_cost: IsCashFlow = field(default=None)
    purchase_cost: IsCashFlow = field(default=None)
    credit: IsCashFlow = field(default=None)
    penalty: IsCashFlow = field(default=None)


@dataclass
class OpnExpense:
    """Cash flow of Operation
    """
    capex: IsCashFlow = field(default=None)
    fopex: IsCashFlow = field(default=None)
    vopex: IsCashFlow = field(default=None)
    incidental: IsCashFlow = field(default=None)


@dataclass
class SpcExpense:
    """CashFlow of Spaces
    """
    land_cost: IsCashFlow = field(default=None)
