""" energiapy.Network - made up of Locations connected by Linkages
"""

from dataclasses import dataclass

from .._component import _Scope


@dataclass
class Network(_Scope):

    def __post_init__(self):
        _Scope.__post_init__(self)

    @property
    def _spatial(self):
        return self

    @staticmethod
    def collection():
        """The collection in scenario"""
        return 'scopes'

    @property
    def locations(self):
        if self._system:
            return self._system.locations
        else:
            return []

    @property
    def linkages(self):
        if self._system:
            return self._system.linkages
        else:
            return []
