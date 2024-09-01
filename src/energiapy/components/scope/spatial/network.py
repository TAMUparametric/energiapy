"""Network is made up of Locations connected by Linkages
"""

from dataclasses import dataclass, field

from ....core._report._syst import (_Cmds, _LnkOpns, _LocOpns,
                                          _Scls, _Spts)
from ..._base._scope import _Scope


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
    label: str = field(default=None)

    def __post_init__(self):
        _Scope.__post_init__(self)

        # if integer number is giver, will make Locations with names node0, node1, ...
        if isinstance(self.locs, int):
            self.locs = [f'node{i}' for i in range(self.locs)]
