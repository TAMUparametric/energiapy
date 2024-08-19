"""Collections of properties to report units of Modeling Blocks
"""

from abc import ABC, abstractmethod


class _Sys(ABC):
    """System"""

    @property
    @abstractmethod
    def system(self):
        """System"""


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
        """Resources of the System"""
        return self.system.resources_stg

    @property
    def materials(self):
        """Materials of the System"""
        return self.system.materials


class _Scps(_Sys):

    @property
    def horizon(self):
        """Horizon of the System"""
        return self.system.horizon

    @property
    def network(self):
        """Network of the System"""
        return self.system.network


class _Alys(_Sys):
    @property
    def players(self):
        """Players of the System"""
        return self.system.players


class _Imps(_Sys):

    @property
    def emissions(self):
        """Emissions of the System"""
        return self.system.emissions


# TODO - Block 5


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


# TODO - Block 6


class _LnkOpns(_Sys):
    """Operations found at Linkage"""

    @property
    def transits(self):
        """Transit Operations of the System"""
        return self.system.transits


# TODO - BLOCK 3


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



# TODO - Block 7


class _Scls(_Sys):
    """Scale"""

    @property
    def scales(self):
        """Temporal Scales of the System"""
        return self.system.scales


class _Prog(ABC):
    """Program"""

    @property
    @abstractmethod
    def program(self):
        """Program"""


# TODO - BLOCK 1


class _Elms(_Prog):
    """Program Elements"""

    @property
    def constraints(self):
        """All Constraints in the Program"""
        return self.program.constraints

    @property
    def variables(self):
        """All Variables in the Program"""
        return self.program.variables

    @property
    def parameters(self):
        """All Parameters in the Program"""
        return self.program.parameters

    @property
    def dispositions(self):
        """All Dispositions in the Program"""
        return self.program.dispositions


class _Dt(ABC):
    """Data"""

    @property
    @abstractmethod
    def data(self):
        """Data"""


# TODO - BLOCK 2


class _Vlus(_Dt):
    """Values of Parameters"""

    @property
    def constants(self):
        """All Constants in the Data"""
        return self.data.constants

    @property
    def datasets(self):
        """All Datasets in the Data"""
        return self.data.datasets

    @property
    def thetas(self):
        """All Thetas in the Data"""
        return self.data.thetas

    @property
    def ms(self):
        """All M in the Data"""
        return self.data.ms

    @property
    def data_all(self):
        """All Data in the Data"""
        return self.data.all
