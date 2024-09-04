"""Network is made up of Locations connected by Linkages
"""

from dataclasses import dataclass, field

from ...core._report._syst import _Cmds, _LnkOpns, _LocOpns, _Scls, _Spts
from .._base._scope import _Scope


class _NtwCols(_Cmds, _LocOpns, _LnkOpns, _Spts, _Scls):
    """Network Collections"""


@dataclass
class Network(_Scope, _NtwCols):
    """Network of Locations and Linkages

    Attributes:
        locs (list[str] | int): Locations in the Network
        label_locs (list[str]): label of Locations
        link_all (bool): link all Locations
        label (str): label of the Network
    """

    locs: list[str] | int = field(default_factory=list)
    label_locs: list[str] = field(default=None)
    link_all: bool = field(default=False)

    def __post_init__(self):
        _Scope.__post_init__(self)

    @property
    def partitions(self):
        """Partitions to divide the Network into"""
        return self.locs

    @property
    def label_partitions(self):
        """Labels for the partitions"""
        return self.label_locs

    @property
    def root(self):
        """Root partition of the Network"""
        return self.locations[0]

    @staticmethod
    def _root():
        """Root partition of the Network"""
        return 'sys'

    @staticmethod
    def _def_name():
        """Default name for the Partitions"""
        return 'node'
