"""Rendition of the Model Data 
"""

from dataclasses import dataclass
from ...core.isalias.elms.isval import IsVal

from ._block import _Block


@dataclass
class Data(_Block):
    """Is the data required for the Model

    set attribures are DataBlock objects

    Attributes:
        name (str): name, takes from the name of the Scenario
    """

    def __post_init__(self):
        _Block.__post_init__(self)

    @property
    def ms(self):
        """Returns the M"""
        return self.fetch('ms')

    @property
    def constants(self):
        """Returns the Constants"""
        return self.fetch('constants')

    @property
    def datasets(self):
        """Returns the DataSets"""
        return self.fetch('datasets')

    @property
    def thetas(self):
        """Returns the Thetas"""
        return self.fetch('thetas')

    @property
    def all(self):
        """Returns all data"""
        return self.ms + self.constants + self.datasets + self.thetas

    def fetch(self, data: str) -> list[IsVal]:
        """Fetches input data of a particular type
        Args:
            data: str: The type of data to fetch [thetas, ms, constants, datasets]
        """
        return sum([getattr(getattr(self, i), data) for i in self.components()], [])
