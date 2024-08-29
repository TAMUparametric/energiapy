"""Base for Operational Components
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from pandas import DataFrame

from ...utils.scaling import scaling
from .._base._defined import _Defined


@dataclass
class _Operational(_Defined, ABC):
    """Base for Operational Components

    Attributes:
        capacity (IsBoundInput): bound on the capacity of the Operation
        land (IsExactInput): land use per Capacity
        material (IsExactInput): material use per Capacity
        capex (IsExactInput): capital expense per Capacity
        opex (IsExactInput): operational expense based on Operation
        emission (IsExactInput): emission due to construction per Capacity
    """

    def __post_init__(self):
        _Defined.__post_init__(self)
        self.operate = self._operate
        if isinstance(self._operate, DataFrame):
            self.operate = scaling(data=self.operate, how='max')
        self._balanced = False

    @property
    @abstractmethod
    def _operate(self):
        """Returns attribute value that signifies operating bounds"""

    @staticmethod
    @abstractmethod
    def _spatials():
        """Spatial Components where the Operation is located"""

    @property
    def spatials(self):
        """Spatial Components where the Operation is located"""
        return getattr(self, self._spatials())

    @property
    @abstractmethod
    def resources(self):
        """Resources used in the Operation"""

    @property
    def materials(self):
        """Materials used in the Operation"""
        if getattr(self, 'use_material'):
            return [
                i.disposition.mat
                for i in getattr(self, 'use_material').spttmpdict.values()
            ]
        else:
            return []

    @property
    def emissions(self):
        """Emissions from the Operation"""
        if getattr(self, 'emission_setup'):
            return [
                i.disposition.emn
                for i in getattr(self, 'emission_setup').spttmpdict.values()
            ]
        else:
            return []

    @property
    def commodities(self):
        """Commodities used in the Operation"""
        return (
            self.materials
            + self.emissions
            + self.resources
            + [self.system.cash]
            + [self.system.land]
        )

    def locate(self):
        """Locates the Component"""

        spatials = self._spatials()
        value = self.spatials

        if value and not isinstance(value, list):
            setattr(self, spatials, [value])

        # If location is not specified, then default to all locations
        if not value:
            setattr(self, spatials, getattr(self._model.system, spatials))
