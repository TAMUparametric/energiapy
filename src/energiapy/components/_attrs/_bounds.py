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
        spend (IsBnd): bound on spending Cash
        earn (IsBnd): bound on earning Cash

    """

    spend: IsBnd = field(default=None)
    earn: IsBnd = field(default=None)


@dataclass
class _EmnBounds:
    """Bounds for Emission

    Attributes:
        emit (IsBnd): bound on Emission

    """

    emit: IsBnd = field(default=None)
    # abate: IsBnd = field(default=None)


@dataclass
class _UsdBounds:
    """Bounds for Land and Material (Used)

    Attributes:
        use (IsBnd): bound on Use Variable

    """

    use: IsBnd = field(default=None)
    # dispose: IsBnd = field(default=None)


@dataclass
class _ResLocBounds:
    """Bounds for Resources at Locations"""

    buy: IsBnd = field(default=None)
    sell: IsBnd = field(default=None)


@dataclass
class _ResLnkBounds:
    """Bounds for Resources at Linkages"""

    ship: IsBnd = field(default=None)
    # only for bi directional linkages
    # receive: IsBnd = field(default=None)


@dataclass
class _ResBounds(_ResLocBounds, _ResLnkBounds):
    """Bounds for Resources

    Attributes:
        buy (IsBnd): bound on amount bought at Location or by Process
        sell (IsBnd): bound on amount sold at Location or by Process
        ship (IsBnd): bound on amount shipped through Linkage
        recieve (IsBnd): bound on amount received through Linkage
    """


@dataclass
class _OpnBounds:
    """Bounds for Operational Components"""

    capacity: IsBnd = field(default=None)


@dataclass
class _ProBounds:
    """Bounds for Process

    Attributes:
        capacity (IsBnd): bound on Capacitate Variable
        produce (IsBnd): bound on Operate Variable
    """

    produce: IsBnd = field(default=None)


@dataclass
class _StgBounds:
    """Bounds for Storage

    Attributes:
        capacity (IsBnd): bound on Capacitate Variable
        store (IsBnd): bound on Store Variable
    """

    store: IsBnd = field(default=None)


@dataclass
class _TrnBounds:
    """Bounds for Transit

    Attributes:
        capacity (IsBnd): bound on Capacitate Variable
        transport (IsBnd): bound on Transport Variable
    """

    transport: IsBnd = field(default=None)
