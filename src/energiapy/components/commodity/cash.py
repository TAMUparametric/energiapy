from dataclasses import dataclass

from .._component import _Commodity


@dataclass
class Cash(_Commodity):
    """Cash derived from:
    Resource Consume and Discharge
    Operation Capacity
    Process Produce
    Storage Store
    Transit Transport
    """

    def __post_init__(self):
        _Commodity.__post_init__(self)

    @staticmethod
    def collection():
        """The collection in scenario"""
        return 'assets'
