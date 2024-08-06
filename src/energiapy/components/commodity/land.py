from dataclasses import dataclass

from .._component import _Commodity


@dataclass
class Land(_Commodity):
    """Land derived from Operation Capacity"""

    def __post_init__(self):
        _Commodity.__post_init__(self)

    @staticmethod
    def collection():
        """The collection in scenario"""
        return 'assets'
