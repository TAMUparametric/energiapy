"""Reports:
System Components
Program Elements
Horizon Discretizations ()
Network Discretizations (Location | Linkage)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..system import System
    from ..program import Program
    from ...components.spatial.network import Network
    from ...components.temporal.horizon import Horizon


class _Report(ABC):
    """Report on System and Program Components"""

    @property
    @abstractmethod
    def system(self) -> System:
        """System Model Block of the Scenario"""

    @property
    @abstractmethod
    def resources(self):
        """Resources of the System"""
        return self.system.resources

    @property
    def cashes(self):
        """Cashes of the System"""
        return self.system.cashes

    @property
    def lands(self):
        """Cashes of the System"""
        return self.system.lands

    @property
    def emissions(self):
        """Emissions of the System"""
        return self.system.emissions

    @property
    def commodities(self):
        """Commodities of the System"""
        return self.system.commodities

    @property
    def processes(self):
        """Processes of the System"""
        return self.system.processes

    @property
    def storages(self):
        """Storages of the System"""
        return self.system.storages

    @property
    def transits(self):
        """Transits of the System"""
        return self.system.transits

    @property
    def operations(self):
        """Operations of the System"""
        return self.system.operations

    @property
    def components(self):
        """Components of the System"""
        return self.system.components

    @property
    @abstractmethod
    def program(self) -> Program:
        """Program Model Block of the Scenario"""
