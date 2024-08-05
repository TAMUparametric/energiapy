from dataclasses import dataclass

from .._initialize._component import _Component


@dataclass
class Emission(_Component):
    """Emission derived from:
    Resource Consume and Discharge
    Material Use
    Operation Capacity
    """

    def __post_init__(self):
        _Component.__post_init__(self)

    @property
    def collection(self):
        """The collection in scenario"""
        return 'emissions'
