
from dataclasses import dataclass

from ...core.inits.component import CmpInit


@dataclass
class Cash(CmpInit):
    """Cash derived from:
        Resource Consume and Discharge
        Operation Capacity
        Process Produce
        Storage Store
        Transit Transport    
    """
    @property
    def collection(self):
        """The collection in scenario
        """
        return 'assets'