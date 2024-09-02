"""Bound Input attributes for all Defined Components
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from ...core.isalias.inps.isinp import IsBnd


class _Ounds(ABC):
    """Abstract Base Class for Bounds"""

    @property
    @abstractmethod
    def plus(self):
        """Positive sign in Balance"""

    @property
    @abstractmethod
    def minus(self):
        """Negative sign in Balance"""


@dataclass
class _PlyB(_Ounds):
    """Bounds for Players

    Attributes:
        has (IsBnd): what a Player has
        needs (IsBnd): what a Player needs

    """

    has: IsBnd = field(default=None)
    needs: IsBnd = field(default=None)

    @property
    def plus(self):
        """Positive sign in Balance"""
        return self.has

    @property
    def minus(self):
        """Negative sign in Balance"""
        return self.needs


@dataclass
class _CshBB(_Ounds):
    """Bounds for Cash

    Attributes:
        spend (IsBnd): bound on spending Cash
        earn (IsBnd): bound on earning Cash

    """

    spend: IsBnd = field(default=None)
    earn: IsBnd = field(default=None)

    @property
    def plus(self):
        """Positive sign in Balance"""
        return self.spend

    @property
    def minus(self):
        """Negative sign in Balance"""
        return self.earn


@dataclass
class _EmnB(_Ounds):
    """Bounds for Emission

    Attributes:
        emit (IsBnd): bound on Emission

    """

    emit: IsBnd = field(default=None)
    abate: IsBnd = field(default=None)

    @property
    def plus(self):
        """Positive sign in Balance"""
        return self.emit

    @property
    def minus(self):
        """Negative sign in Balance"""
        return self.abate


@dataclass
class _UsdB(_Ounds):
    """Bounds for Land and Material (Used)

    Attributes:
        use (IsBnd): bound on Use Variable

    """

    use: IsBnd = field(default=None)
    dispose: IsBnd = field(default=None)

    @property
    def plus(self):
        """Positive sign in Balance"""
        return self.use

    @property
    def minus(self):
        """Negative sign in Balance"""
        return self.dispose


@dataclass
class _ResLocB(_Ounds):
    """Bounds for Resources at Locations"""

    buy: IsBnd = field(default=None)
    sell: IsBnd = field(default=None)

    @property
    def plus(self):
        """Positive sign in Balance"""
        return self.buy

    @property
    def minus(self):
        """Negative sign in Balance"""
        return self.sell


@dataclass
class _ResLnkBB(_Ounds):
    """Bounds for Resources at Linkages"""

    ship: IsBnd = field(default=None)
    # only for bi directional linkages
    receive: IsBnd = field(default=None)


@dataclass
class _ResBounds(_ResLocBB(_Ounds), _ResLnkBB(_Ounds)):
    """Bounds for Resources

    Attributes:
        buy (IsBnd): bound on amount bought at Location or by Process
        sell (IsBnd): bound on amount sold at Location or by Process
        ship (IsBnd): bound on amount shipped through Linkage
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
