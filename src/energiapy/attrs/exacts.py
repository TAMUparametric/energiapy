"""Exact input attributes for Components
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.aliases.is_input import IsExactInput


class ExpExacts:
    """Exact input attributes for Components"""

    @classmethod
    def expenses(cls):
        """Exact Inputs across the Scenario"""
        return fields(cls)


class EmnExacts:
    """Exact Emission Inputs for Components"""

    @classmethod
    def emitted(cls):
        """Exact Emission Inputs across the Scenario"""
        return fields(cls)


class UseExacts:
    """Exact Use Inputs for Components"""

    @classmethod
    def used(cls):
        """Exact Use Inputs across the Scenario"""
        return fields(cls)


# Resource


@dataclass
class ResExpExacts(ExpExacts):
    """Exact Expense Inputs for Resources"""

    price_buy: IsExactInput = field(default=None)
    price_sell: IsExactInput = field(default=None)
    credit: IsExactInput = field(default=None)
    penalty: IsExactInput = field(default=None)


@dataclass
class ResEmnExacts(EmnExacts):
    """Exact Emission Inputs for Resources"""

    emission_buy: IsExactInput = field(default=None)
    emission_sell: IsExactInput = field(default=None)
    emission_loss: IsExactInput = field(default=None)


@dataclass
class ResExacts(ResExpExacts, ResEmnExacts):
    """Exact Inputs for Resources"""


# Land and Material (Used)


@dataclass
class UsedExpExacts(ExpExacts):
    """Exact Expense Inputs for Land and Material (Used)"""

    cost_use: IsExactInput = field(default=None)


@dataclass
class UsedEmnExacts(EmnExacts):
    """Exact Emissions Inputs for Land and Material (Used)"""

    emission_use: IsExactInput = field(default=None)


@dataclass
class UsedExacts(UsedExpExacts, UsedEmnExacts):
    """Exact Inputs for Land and Material (Used)"""


# Operational (Process, Storage, Transit)


@dataclass
class OpnExpExacts(ExpExacts):
    """Exact Expense Inputs for Operational Components"""

    capex: IsExactInput = field(default=None)
    opex: IsExactInput = field(default=None)


@dataclass
class OpnEmnExacts(EmnExacts):
    """Exact Emission Inputs for Operational Components"""

    emission_setup: IsExactInput = field(default=None)


@dataclass
class OpnUseExacts(UseExacts):
    """Exact Use Inputs for Operational Components"""

    use_land: IsExactInput = field(default=None)
    use_material: IsExactInput = field(default=None)


@dataclass
class OpnExacts(OpnExpExacts, OpnEmnExacts, OpnUseExacts):
    """Exact Inputs for Operational Components"""


@dataclass
class ProExacts(OpnExacts):
    """Exact Inputs for Process Components"""


@dataclass
class StgExacts(OpnExacts):
    """Exact Inputs for Storage Components"""

    loss_storage: IsExactInput = field(default=None)


@dataclass
class TrnExacts(OpnExacts):
    """Exact Inputs for Transit Components"""

    loss_transit: IsExactInput = field(default=None)
    speed: IsExactInput = field(default=None)
