
from dataclasses import dataclass

from .._component import _Component


@dataclass
class Cash(_Component):
    """Cash derived from:
        Resource Consume and Discharge
        Operation Capacity
        Process Produce
        Storage Store
        Transit Transport    
    """

    def __post_init__(self):
        _Component.__post_init__(self)

    @property
    def collection(self):
        """The collection in scenario
        """
        return 'assets'
