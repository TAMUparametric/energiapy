from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .aspect import Aspect
from .capacity import Capacity
from .resflow import Consume, Discharge
from .resflowcap import Produce

if TYPE_CHECKING:
    from ...type.alias import IsCash, IsCashFlow


@dataclass
class CashFlow(Aspect):
    """Cash flow
    """
    cash: IsCash = field(default=None)
    cost: IsCashFlow = field(default=None)


@dataclass
class SellCost(CashFlow, Discharge):
    """Selling cost
    """


@dataclass
class BuyCost(CashFlow, Consume):
    """Buying cost
    """

# TODO - add the rest


@dataclass
class Capex(CashFlow, Capacity):
    """Operation capital expenditure
    """
    
@dataclass
class Fopex(CashFlow, Capacity):
    """Operation fixed operational expenditure
    """

@dataclass
class Vopex(CashFlow, Produce):
    """Operation variable operational expenditure
    """

