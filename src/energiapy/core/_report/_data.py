"""Properties to report Data Modeling Block Values
"""

from abc import ABC, abstractmethod

class _Vlus(ABC):
    """Values of Parameters"""

    @property
    @abstractmethod
    def data(self):
        """Data"""

    @property
    def constants(self):
        """All Constants in the Data"""
        return self.data.constants

    @property
    def datasets(self):
        """All Datasets in the Data"""
        return self.data.datasets

    @property
    def thetas(self):
        """All Thetas in the Data"""
        return self.data.thetas

    @property
    def ms(self):
        """All M in the Data"""
        return self.data.ms

    @property
    def data_all(self):
        """All Data in the Data"""
        return self.data.all
