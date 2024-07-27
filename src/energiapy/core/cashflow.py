from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..type.alias import IsCashFlow, IsPWL


@dataclass
class RscCashFlow:
    """Cash flow of Commodities
    """
    sell_cost: IsCashFlow = field(default=None)
    purchase_cost: IsCashFlow = field(default=None)
    credit: IsCashFlow = field(default=None)
    penalty: IsCashFlow = field(default=None)


@dataclass
class OpnCashFlow:
    """Cash flow of Operations
    """
    capex: IsCashFlow = field(default=None)
    capex_pwl: IsPWL = field(default=None)
    fopex: IsCashFlow = field(default=None)
    vopex: IsCashFlow = field(default=None)
    incidental: IsCashFlow = field(default=None)


@dataclass
class PrcCashFlow(OpnCashFlow, RscCashFlow):
    """Cash flow of Processes
    """


@dataclass
class StrCashFlow(OpnCashFlow):
    """Cash flow of Storages
    """
    storage_cost: IsCashFlow = field(default=None)


@dataclass
class SptCashFlow(OpnCashFlow):
    """CashFlow of Spaces
    """
    land_cost: IsCashFlow = field(default=None)
