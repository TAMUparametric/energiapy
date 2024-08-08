""" energiapy.Network - made up of Locations connected by Linkages
"""

from dataclasses import dataclass, field
from typing import List, Union

from .._component import _Scope


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

    @staticmethod
    def collection():
        """The collection in scenario"""
        return 'scopes'

    @property
    def locations(self):
        return self._system.locations

    @property
    def linkages(self):
        return self._system.linkages

    @property
    def nodes(self):
        return self.locations

    @property
    def edges(self):
        return self.linkages