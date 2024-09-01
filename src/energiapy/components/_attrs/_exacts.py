"""Exact input attributes for Components
"""

from dataclasses import dataclass, field

from ...core.isalias.inps.isinp import IsExt, IsInc

# -------------Transact Exacts-------------


@dataclass
class _ResTscExacts:
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
class _UsdTscExacts:
    """Exact Transact Inputs for Land and Material (Used)

    Attributes:
        use_cost (IsInc): cost associated with using Land or Material (Used)
    """

    use_cost: IsInc = field(default=None)


@dataclass
class _OpnTscExacts:
    """Exact Transact Inputs for Operational Components

    Attributes:
        capex (IsInc): capital expenditure associated with setting up Operational Component
        opex (IsInc): operational expenditure associated with operation of Operational Component
    """

    capex: IsInc = field(default=None)
    opex: IsInc = field(default=None)


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


# -------------UseStp Exacts-------------


@dataclass
class _OpnUseExacts:
    """Exact Use Inputs for Operational Components

    Attributes:
        setup_use (IsExt): use (Material or Land) associated with setting up Operational Component

    """

    setup_use: IsExt = field(default=None)


# -------------Loss Exacts-------------


@dataclass
class _StgLseExacts:
    """Exact Loss during inventory of Resource by Storage

    Attributes:
        inventory_loss (IsExt): loss associated with storing Resource

    """

    inventory_loss: IsExt = field(default=None)


@dataclass
class _TrnLseExacts:
    """Exact Loss during freight of Resource by Transit

    Attributes:
        freight_loss (IsExt): loss associated with transporting Resource

    """

    freight_loss: IsExt = field(default=None)


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


# -------------Exacts Component-wise -------------
# These are inherited by the Components


@dataclass
class _ResExacts(_ResTscExacts, _ResEmnExacts):
    """Exact Inputs for Resources imported by Process"""


@dataclass
class _UsdExacts(_UsdTscExacts, _UsdEmnExacts):
    """Exact Inputs for Land and Material (Used)"""


@dataclass
class _OpnExacts(_OpnTscExacts, _OpnEmnExacts, _OpnUseExacts, _OpnRteExacts):
    """Exact Inputs for Operational Components"""


@dataclass
class _ProExacts(_OpnExacts):
    """Exact Inputs for Process Components"""


@dataclass
class _StgExacts(_OpnExacts, _StgLseExacts):
    """Exact Inputs for Storage Components"""


@dataclass
class _TrnExacts(_OpnExacts, _TrnLseExacts, _TrnRteExacts):
    """Exact Inputs for Transit Components"""


# -------------Exacts Task-wise -------------
# These are used by the TaskMaster to generate Tasks


@dataclass
class _TscExacts(_ResTscExacts, _UsdTscExacts, _OpnTscExacts):
    """Exact Transact Inputs for Components"""


@dataclass
class _EmnExacts(_ResEmnExacts, _UsdEmnExacts, _OpnEmnExacts):
    """Exact Emission Inputs for Components"""


@dataclass
class _UseExacts(_OpnUseExacts):
    """Exact Use Inputs for Components"""


@dataclass
class _LseExacts(_StgLseExacts, _TrnLseExacts):
    """Exact Loss Inputs for Components"""


@dataclass
class _RteExacts(_OpnRteExacts, _TrnRteExacts):
    """Exact Rate Inputs for Components"""
