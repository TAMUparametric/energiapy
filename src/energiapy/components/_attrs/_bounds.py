"""Bound Input attributes for all Defined Components
"""

from dataclasses import dataclass, field

from ...core.isalias.inps.isinp import IsBnd


@dataclass
class _PlyBounds:
    """Bounds for Players

    Attributes:
        has (IsBnd): what a Player has
        needs (IsBnd): what a Player needs

    """

    has: IsBnd = field(default=None)
    needs: IsBnd = field(default=None)


@dataclass
class _CshBounds:
    """Bounds for Cash

    Attributes:
        spend (IsBnd): bound on spending
        earn (IsBnd): bound on earning

    """

    spend: IsBnd = field(default=None)
    earn: IsBnd = field(default=None)


@dataclass
class _EmnBounds:
    """Bounds for Emission

    Attributes:
        emit (IsBnd): bound on how much is discharged
        sequester (IsBnd): bound on how much is abated

    """

    emit: IsBnd = field(default=None)
    sequester: IsBnd = field(default=None)


@dataclass
class _UsdBounds:
    """Bounds for Land and Material (Used)

    Attributes:
        use (IsBnd): bound on how much is used
        dispose (IsBnd): bound on how much is disposed
    """

    use: IsBnd = field(default=None)
    dispose: IsBnd = field(default=None)


@dataclass
class _ResBounds:
    """Bounds for Resources

    Attributes:
        buy (IsBnd): bound on amount bought at Location
        sell (IsBnd): bound on amount sold at Location
        ship (IsBnd): bound on amount shipped from Linkage
        recieve (IsBnd): bound on amount recieved from Linkage
        lose (IsBnd): bound on amount lost at Location or Linkage
        recover (IsBnd): bound on amount recovered at Location or between Linkage
    """

    # Trade at Locations
    buy: IsBnd = field(default=None)
    sell: IsBnd = field(default=None)
    # Trade between Linkages
    ship: IsBnd = field(default=None)
    # Lose at Location or between Linkage
    lose: IsBnd = field(default=None)


@dataclass
class _OpnBounds:
    """Bounds for Operational Components

    Attributes:
        setup (IsBnd): bound on how much capacity can be setup
        dismantle (IsBnd): bound on how much capacity can be dismantled
    """

    setup: IsBnd = field(default=None)
    dismantle: IsBnd = field(default=None)


