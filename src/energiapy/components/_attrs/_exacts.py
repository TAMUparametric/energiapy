"""Exact input attributes for Components
"""

from dataclasses import dataclass, field

from ...core.aliases.inps.isinp import IsExt, IsInc

# -------------Transact Exacts-------------


@dataclass
class _ResExpExacts:
    """Exact Transact Inputs for Resources


    Attributes:
        buy_price (IsInc): price associated with buying Resource
        sell_price (IsInc): price associated with selling Resource
        credit (IsExt): credit associated with selling Resource
        penalty (IsExt): penalty associated with not meeting the lower bound for selling Resource

    """

    buy_price: IsInc = field(default=None)
    sell_price: IsInc = field(default=None)
    credit: IsExt = field(default=None)
    penalty: IsExt = field(default=None)


@dataclass
class _UsdExpExacts:
    """Exact Transact Inputs for Land and Material (Used)

    Attributes:
        use_cost (IsInc): cost associated with using Land or Material (Used)
    """

    use_cost: IsInc = field(default=None)


@dataclass
class _OpnExpExacts:
    """Exact Transact Inputs for Operational Components

    Attributes:
        capex (IsInc): capital expenditure associated with setting up Operational Component
        opex (IsInc): operational expenditure associated with operation of Operational Component
    """

    capex: IsInc = field(default=None)
    opex: IsInc = field(default=None)


@dataclass
class _ExpExacts(_ResExpExacts, _UsdExpExacts, _OpnExpExacts):
    """Exact Transact Inputs for Components"""


# -------------Emission Exacts-------------


@dataclass
class _ResEmnExacts:
    """Exact Emission Inputs for Resources

    Attributes:
        buy_emission (IsExt): emission associated with buying Resource
        sell_emission (IsExt): emission associated with selling Resource
        loss_emission (IsExt): emission associated with losing Resource

    """

    buy_emission: IsExt = field(default=None)
    sell_emission: IsExt = field(default=None)
    loss_emission: IsExt = field(default=None)


@dataclass
class _UsdEmnExacts:
    """Exact Emissions Inputs for Land and Material (Used)

    Attributes:
        use_emission (IsExt): emission associated with using Land or Material (Used

    """

    use_emission: IsExt = field(default=None)


@dataclass
class _OpnEmnExacts:
    """Exact Emission Inputs for Operational Components

    Attributes:
        setup_emission (IsExt): emission associated with setting up Operational Component

    """

    setup_emission: IsExt = field(default=None)


@dataclass
class _EmnExacts(_ResEmnExacts, _UsdEmnExacts, _OpnEmnExacts):
    """Exact Emission Inputs for Components"""


# -------------UseSetUp Exacts-------------


@dataclass
class _UsdUseExacts:
    """Exact Uses of Land and Material (Used) by Operational Components

    Attributes:
        land_use (IsExt): land use associated with setting up Operational Component
        material_use (IsExt): material use associated with setting up Operational Component

    """

    land_use: IsExt = field(default=None)
    material_use: IsExt = field(default=None)


@dataclass
class _UsdExpExacts:
    """Exact Use Costs for Land and Material (Used) by Operational Components

    Attributes:
        land_use_cost (IsExt): cost associated with using Land for setting up Operational Component
        material_use_cost (IsExt): cost associated with using Material (Used) for setting up Operational Component

    """

    land_use_cost: IsExt = field(default=None)
    material_use_cost: IsExt = field(default=None)


@dataclass
class _UsdEmnExacts:
    """Exact Use Emissions by use of Land and Material (Used) by Operational Components

    Attributes:
        land_use_emission (IsExt): emission associated with using Land for setting up Operational Component
        material_use_emission (IsExt): emission associated with using Material (Used) for setting up Operational Component

    """

    land_use_emission: IsExt = field(default=None)
    material_use_emission: IsExt = field(default=None)


@dataclass
class _UsdExacts(_UsdUseExacts, _UsdExpExacts, _UsdEmnExacts):
    """Exact Use Inputs for Operational Components"""


# -------------Loss Exacts-------------


@dataclass
class _StgLssExacts:
    """Exact Loss during inventory of Resource by Storage

    Attributes:
        inventory_loss (IsExt): loss associated with storing Resource

    """

    inventory_loss: IsExt = field(default=None)


@dataclass
class _TrnLssExacts:
    """Exact Loss during freight of Resource by Transit

    Attributes:
        freight_loss (IsExt): loss associated with transporting Resource

    """

    freight_loss: IsExt = field(default=None)


@dataclass
class LssExacts(_StgLssExacts, _TrnLssExacts):
    """Exact Loss Inputs for Components"""


# -------------Rate Exacts-------------


@dataclass
class _OpnRteExacts:
    """Exact Rate Inputs for Operational Components

    Attributes:
        setup_time (IsExt): time associated with setting up Operational Component

    """

    setup_time: IsExt = field(default=None)


@dataclass
class _TrnRteExacts:
    """Exact Rate Inputs for Transit

    Attributes:
        speed (IsExt): speed associated with transporting Resource

    """

    speed: IsExt = field(default=None)


@dataclass
class _RteExacts(_OpnRteExacts, _TrnRteExacts):
    """Exact Rate Inputs for Components"""


# -------------Component Exacts-------------


@dataclass
class _ResExacts(_ResExpExacts, _ResEmnExacts):
    """Exact Inputs for Resources imported by Process"""


@dataclass
class _UsdExacts(_UsdExpExacts, _UsdEmnExacts):
    """Exact Inputs for Land and Material (Used)"""


@dataclass
class _OpnExacts(_OpnExpExacts, _OpnEmnExacts, _UsdExacts, _OpnRteExacts):
    """Exact Inputs for Operational Components"""


@dataclass
class _ProExacts(_OpnExacts):
    """Exact Inputs for Process Components"""


@dataclass
class _StgExacts(_OpnExacts, _StgLssExacts):
    """Exact Inputs for Storage Components"""


@dataclass
class _TrnExacts(_OpnExacts, _TrnLssExacts, _TrnRteExacts):
    """Exact Inputs for Transit Components"""
