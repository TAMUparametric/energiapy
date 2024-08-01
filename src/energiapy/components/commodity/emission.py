from dataclasses import dataclass

from ...core.inits.component import CmpInit


@dataclass
class Emission(CmpInit):
    """Emission derived from:
        Resource Consume and Discharge
        Material Use
        Operation Capacity
    """
    @property
    def collection(self):
        """The collection in scenario
        """
        return 'emissions'
