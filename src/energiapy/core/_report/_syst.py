"""Properties to report System Modeling Block Components
"""

from abc import ABC, abstractmethod


class _Sys(ABC):
    """System"""

    @property
    @abstractmethod
    def system(self):
        """System"""


class _Alys(_Sys):
    
    @property
    def players(self):
        """Players of the System"""
        return self.system.players


class _Cmds(_Sys):

    @property
    def cash(self):
        """Cash of the System"""
        return self.system.cash

    @property
    def land(self):
        """Land of the System"""
        return self.system.land

    @property
    def resources(self):
        """Resources of the System"""
        return self.system.resources

    @property
    def resources_stg(self):
        """Resources in Inventory of the System"""
        return self.system.resources_stg

    @property
    def resources_trn(self):
        """Resources in Transit of the System"""
        return self.system.resources_trn

    @property
    def materials(self):
        """Materials of the System"""
        return self.system.materials

    @property
    def emissions(self):
        """Emissions of the System"""
        return self.system.emissions

    @property
    def commodities(self):
        """Commodities of the System"""
        return self.system.commodities


class _Scps(_Sys):

    @property
    def horizon(self):
        """Horizon of the System"""
        return self.system.horizon

    @property
    def network(self):
        """Network of the System"""
        return self.system.network


class _LocOpns(_Sys):
    """Operations found at Location"""

    @property
    def processes(self):
        """Process Operations of the System"""
        return self.system.processes

    @property
    def storages(self):
        """Storage Operations of the System"""
        return self.system.storages


class _LnkOpns(_Sys):
    """Operations found at Linkage"""

    @property
    def transits(self):
        """Transit Operations of the System"""
        return self.system.transits


class _Opns(_LocOpns, _LnkOpns):
    """Operations"""

    @property
    def operations(self):
        """Operations of the System"""
        return self.system.operations


class _Spts(_Sys):
    """Spatial Components"""

    @property
    def locations(self):
        """Locations of the System"""
        return self.system.locations

    @property
    def linkages(self):
        """Linkages of the System"""
        return self.system.linkages

    @property
    def nodes(self):
        """Nodes of the System"""
        return self.system.nodes

    @property
    def edges(self):
        """Edges of the System"""
        return self.system.edges

    @property
    def sources(self):
        """Source Locations of the System"""
        return self.system.sources

    @property
    def sinks(self):
        """Sink Locations of the System"""
        return self.system.sinks

    @property
    def pairs(self):
        """Source Sink pairs of the System"""
        return self.system.pairs

    @property
    def spatials(self):
        """Spatial Components of the System"""
        return self.system.spatials


class _Scls(_Sys):
    """Scale"""

    @property
    def scales(self):
        """Temporal Scales of the System"""
        return self.system.scales


class _Cmps(_Alys, _Cmds, _Scps, _Opns, _Spts, _Scls):
    """Components"""
