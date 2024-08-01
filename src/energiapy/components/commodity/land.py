
from dataclasses import dataclass

from ...core.inits.component import CmpInit


@dataclass
class Land(CmpInit):
    """Land derived from Operation Capacity
    """
    @property
    def collection(self):
        """The collection in scenario
        """
        return 'assets'
