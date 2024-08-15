"""There are user defined components
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field  # , fields
from typing import TYPE_CHECKING

# from ..._core._nirop._error import CacodcarError
# from ...constraints.taskmaster import taskmaster
from ._component import _Component
from ._consistent import _Consistent

if TYPE_CHECKING:
    from ..._core._aliases._is_input import IsBoundInput, IsExactInput


@dataclass
class _Defined(_Component, _Consistent, ABC):
    """Common initial attributes of components"""

    basis: str = field(default='unit')
    citation: dict = field(default=None)  # TODO - for each attribute make dict
    block: str = field(default=None)
    introduce: str = field(default=None)
    retire: str = field(default=None)
    label: str = field(default=None)

    def __post_init__(self):
        _Component.__post_init__(self)
        self.ctypes = []
        self._consistent = False

        # attrs_task = set(list(taskmaster[self.collection()]))
        # attrs_fields = set([i.name for i in fields(self)])
        # if not attrs_task <= attrs_fields:
        #     print('defined tasks:', attrs_task)
        #     print('component fields:', attrs_fields)
        #     raise CacodcarError(f'{self}: attributes not in fields')

    @staticmethod
    @abstractmethod
    def collection():
        """reports what collection the Component belongs to"""

    @staticmethod
    @abstractmethod
    def bounds():
        """Attrs that quantify the bounds of the Component"""

    @classmethod
    @abstractmethod
    def inputs(cls):
        """Attrs"""

    @classmethod
    @abstractmethod
    def _cnst_csh(cls):
        """Adds Cash when making consistent"""

    @classmethod
    @abstractmethod
    def _cnst_lnd(cls):
        """Adds Land when making consistent"""

    @classmethod
    @abstractmethod
    def _cnst_nstd(cls):
        """Is a nested input to be made consistent"""

    @classmethod
    @abstractmethod
    def _cnst_nstd_csh(cls):
        """Is a nested input to be made consistent with Cash"""

    @property
    def _horizon(self):
        """The Horizon of the Component"""
        return self._system.horizon

    @property
    def _network(self):
        """The Network of the Component"""
        return self._system.network

    @property
    def _cash(self):
        """The Cash of the Component"""
        return self._system.cash

    @property
    def _land(self):
        """The Land of the Component"""
        return self._system.land

    @property
    def data(self):
        """Returns the data of the component"""
        return getattr(self._data, self.name)

    @property
    def datasets(self):
        """Returns the DataSets"""
        return self.data.datasets

    @property
    def ms(self):
        """Returns the Ms"""
        return self.data.ms

    @property
    def thetas(self):
        """Returns the Thetas"""
        return self.data.thetas

    @property
    def constants(self):
        """Returns the Constants"""
        return self.data.constants

    def make_consistent(self):
        """Makes the data inputs consistent IsSptTmpDict"""
        for attr in self.inputs():
            value = getattr(self, attr)

            if value is not None:

                if attr in self.bounds():
                    setattr(self, attr, self.make_spttmpdict(value))

                if attr in self._cnst_csh():
                    setattr(self, attr, {self._cash: self.make_spttmpdict(value)})

                if attr in self._cnst_lnd():
                    setattr(self, attr, {self._land: self.make_spttmpdict(value)})

                if attr in self._cnst_nstd():
                    setattr(
                        self,
                        attr,
                        {i: self.make_spttmpdict(j) for i, j in value.items()},
                    )

                if attr in self._cnst_nstd_csh():
                    setattr(
                        self,
                        attr,
                        {
                            i: {self._cash: self.make_spttmpdict(j)}
                            for i, j in value.items()
                        },
                    )

        self._consistent = True
