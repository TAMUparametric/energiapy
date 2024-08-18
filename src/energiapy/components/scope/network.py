""" energiapy.Network - made up of Locations connected by Linkages
"""

from dataclasses import dataclass, field
from typing import List, Union

from ._scope import _Scope


@dataclass
class Network(_Scope):
    """Network of Locations and Linkages"""

    locs: Union[List[str], int] = field(default_factory=list)
    label_locs: List[str] = field(default=None)
    link_all: bool = field(default=True)
    label: str = field(default=None)

    def __post_init__(self):
        _Scope.__post_init__(self)
        if isinstance(self.locs, int):
            self.locs = [f'node{i}' for i in range(self.locs)]

    # TODO - Block 3
    @property
    def locations(self):
        return self.system.locations

    @property
    def linkages(self):
        return self.system.linkages

    @property
    def nodes(self):
        return self.locations

    @property
    def edges(self):
        return self.linkages
