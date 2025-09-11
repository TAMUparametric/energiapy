"""Default decisions"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...dimensions.decisiontree import DecisionTree
    from ..constraints.bind import Bind


class Get(ABC):
    """Get the Decision"""

    @property
    @abstractmethod
    def tree(self) -> DecisionTree:
        """Decision Tree"""

    # The decision is pulled from the tree with the component as the default index
    def get(self, decision: str) -> Bind:
        """Get the decision"""
        return getattr(self.tree, decision)(self)


# -------------------------------------------------------
# Design
# -------------------------------------------------------
class Capacity(Get):
    """Operational Capacity of an Operation"""

    @property
    def capacity(self):
        """Operational Capacity"""
        return self.get('capacity')

    @property
    def operate(self):
        """Capacity Utilization"""
        return self.get('operate')


class Capacitate(Get):
    """Capacitate an Operation"""

    @property
    def setup(self):
        """Add Capacity"""
        return self.get('setup')

    @property
    def dismantle(self):
        """Remove Capacity"""
        return self.get('dismantle')


class Design(Capacity, Capacitate):
    """Design an Operation"""


# -------------------------------------------------------
# Scheduling
# -------------------------------------------------------


class Operate(Get):
    """Operate an Operation"""

    @property
    def operate(self):
        return self.get('operate')


class Ramp(Get):
    """Ramp an Operation"""

    @property
    def rampup(self):
        return self.get('rampup')

    @property
    def rampdown(self):
        return self.get('rampdown')


class Scheduling(Operate, Ramp):
    """Schedule an Operation"""


# -------------------------------------------------------
# Inventory
# -------------------------------------------------------


class InvCapacity(Get):
    """Inventory Capacity of a Resource"""

    @property
    def invcapacity(self):
        """Inventory Capacity"""
        return self.get('invcapacity')


class InvCapacitate(Get):
    """Capacitate an Operation"""

    @property
    def invsetup(self):
        """Add Capacity"""
        return self.get('invsetup')

    @property
    def invdismantle(self):
        """Remove Capacity"""
        return self.get('invdismantle')


class Stock(Get):
    """Inventory of a Resource"""

    @property
    def inventory(self):
        return self.get('inventory')


class Inventory(InvCapacity, InvCapacitate, Stock):
    """Inventory a Resource"""


# -------------------------------------------------------
# Trade
# -------------------------------------------------------


class Trade(Get):
    """Exchange Resource/Material with another Player"""

    @property
    def buy(self):
        return self.get('buy')

    @property
    def sell(self):
        return self.get('sell')


class Transact(Get):
    """Exchange Currency with another Player"""

    @property
    def earn(self):
        return self.get('earn')

    @property
    def spend(self):
        return self.get('spend')


# -------------------------------------------------------
# Streams
# -------------------------------------------------------


class Produce(Get):
    """Resource Stream resulting from Operate"""

    @property
    def produce(self):
        return self.get('produce')

    @property
    def expend(self):
        return self.get('expend')


class Free(Get):
    """Free Resource Stream"""

    @property
    def consume(self):
        return self.get('consume')

    @property
    def release(self):
        return self.get('release')


class Ship(Get):
    """Resource Stream between Locations"""

    @property
    def ship_out(self):
        return self.get('ship_out')


class EnvImp(Get):
    """Environemntal Impact"""

    @property
    def emit(self):
        return self.get('emit')

    @property
    def abate(self):
        return self.get('abate')

    @property
    def change(self):
        return self.get('change')


class SocImp(Get):
    """Soc Impact"""

    @property
    def benefit(self):
        return self.get('benefit')

    @property
    def detriment(self):
        return self.get('detriment')

    @property
    def success(self):
        return self.get('success')


class EcoImp(Get):
    """Economic Impact"""

    @property
    def income(self):
        return self.get('income')

    @property
    def expense(self):
        return self.get('expense')

    @property
    def revenue(self):
        return self.get('revenue')


class Utilize(Get):
    """Usage of a Material"""

    @property
    def use(self):
        return self.get('use')

    @property
    def dispose(self):
        return self.get('dispose')
