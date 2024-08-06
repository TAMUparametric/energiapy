""" energiapy.Location
"""

from dataclasses import dataclass

from .._component import _Spatial


@dataclass
class Location(_Spatial):
    """Location where Process and Storage can reside"""

    def __post_init__(self):
        _Spatial.__post_init__(self)
        for i in ['processes', 'storages', 'resources', 'materials', 'cash', 'land']:
            setattr(self, i, [])

    # TODO - check this property
    @property
    def _spatial(self):
        return self

    @staticmethod
    def collection():
        """The collection in scenario"""
        return 'locations'
