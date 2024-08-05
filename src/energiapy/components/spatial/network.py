""" energiapy.Network - made up of Locations connected by Linkages
"""

from dataclasses import dataclass

from .._component import _ScopeComponent


@dataclass
class Network(_ScopeComponent):

    def __post_init__(self):
        _ScopeComponent.__post_init__(self)
        self.locations, self.linkages = [], []

    @property
    def _spatial(self):
        return self

    @property
    def collection(self):
        """The collection in scenario"""
        return 'network'
