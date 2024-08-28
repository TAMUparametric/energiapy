"""Exact input attributes for Components
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.aliases.is_input import IsExactInput


# -------------Expense Exacts-------------


@dataclass
class ResExpExacts:
    """Exact Expense Inputs for Resources"""

    price_buy: IsExactInput = field(default=None)
    price_sell: IsExactInput = field(default=None)
    credit: IsExactInput = field(default=None)
    penalty: IsExactInput = field(default=None)


@dataclass
class UsedExpExacts:
    """Exact Expense Inputs for Land and Material (Used)"""

    cost_use: IsExactInput = field(default=None)


@dataclass
class OpnExpExacts:
    """Exact Expense Inputs for Operational Components"""

    capex: IsExactInput = field(default=None)
    opex: IsExactInput = field(default=None)


@dataclass
class ExpExacts(ResExpExacts, UsedExpExacts, OpnExpExacts):
    """Exact Expense Inputs for Components"""


# -------------Emission Exacts-------------


@dataclass
class ResEmnExacts:
    """Exact Emission Inputs for Resources"""

    emission_buy: IsExactInput = field(default=None)
    emission_sell: IsExactInput = field(default=None)
    emission_loss: IsExactInput = field(default=None)


@dataclass
class UsedEmnExacts:
    """Exact Emissions Inputs for Land and Material (Used)"""

    emission_use: IsExactInput = field(default=None)


@dataclass
class OpnEmnExacts:
    """Exact Emission Inputs for Operational Components"""

    emission_setup: IsExactInput = field(default=None)


@dataclass
class EmnExacts(ResEmnExacts, UsedEmnExacts, OpnEmnExacts):
    """Exact Emission Inputs for Components"""


# -------------Use exacts-------------


@dataclass
class UsgExacts:
    """Exact Use Inputs for Operational Components"""

    use_land: IsExactInput = field(default=None)
    use_material: IsExactInput = field(default=None)


# -------------Loss Exacts-------------


@dataclass
class StgLossExacts:
    """Exact Loss Inputs for Storage Components"""

    loss_storage: IsExactInput = field(default=None)


@dataclass
class TrnLossExacts:
    """Exact Loss Inputs for Transit Components"""

    loss_transit: IsExactInput = field(default=None)


@dataclass
class LssExacts(StgLossExacts, TrnLossExacts):
    """Exact Loss Inputs for Components"""


# -------------Rate Exacts-------------


@dataclass
class RteExacts:
    """Exact Rate Inputs for Transit Components"""

    speed: IsExactInput = field(default=None)


# -------------Component Exacts-------------


@dataclass
class ResExacts(ResExpExacts, ResEmnExacts):
    """Exact Inputs for Resources"""


@dataclass
class UsedExacts(UsedExpExacts, UsedEmnExacts):
    """Exact Inputs for Land and Material (Used)"""


class OpnExacts(OpnEmnExacts, UsgExacts, ABC):
    """Exact Inputs for Operational Components"""

    @property
    @abstractmethod
    def system(self):
        """System of the Operation"""

    @property
    @abstractmethod
    def resources(self):
        """Resources used in the Operation"""


@dataclass
class ProExacts(OpnExpExacts, OpnExacts):
    """Exact Inputs for Process Components"""


@dataclass
class StgExacts(OpnExpExacts, OpnExacts, StgLossExacts):
    """Exact Inputs for Storage Components"""


@dataclass
class TrnExacts(OpnExpExacts, OpnExacts, TrnLossExacts, RteExacts):
    """Exact Inputs for Transit Components"""
