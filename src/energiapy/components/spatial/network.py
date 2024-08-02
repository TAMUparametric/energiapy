""" energiapy.Network - made up of Locations connected by Linkages
"""

from dataclasses import dataclass

from ...core.inits.component import CmpInit


@dataclass
class Network(CmpInit):

    def __post_init__(self):
        CmpInit.__post_init__(self)
        self.locations, self.linkages = [], []

    @property
    def collection(self):
        """The collection in scenario
        """
        return 'network'
