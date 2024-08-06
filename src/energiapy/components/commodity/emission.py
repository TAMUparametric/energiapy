from dataclasses import dataclass

from .._component import _Commodity


@dataclass
class Emission(_Commodity):
    """Emission derived from:
    Resource Consume and Discharge
    Material Use
    Operation Capacity
    """

    def __post_init__(self):
        _Commodity.__post_init__(self)

    @staticmethod
    def collection():
        """The collection in scenario"""
        return 'emissions'
