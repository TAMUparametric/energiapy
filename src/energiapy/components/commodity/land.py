from dataclasses import dataclass

from .._component import _Component


@dataclass
class Land(_Component):
    """Land derived from Operation Capacity"""

    def __post_init__(self):
        _Component.__post_init__(self)

    @property
    def collection(self):
        """The collection in scenario"""
        return 'assets'
