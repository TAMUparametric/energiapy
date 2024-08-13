"""There are user defined components
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, fields
from typing import TYPE_CHECKING

from ..._core._layout._action import action
from ..._core._layout._nature import nature
from ..._core._nirop._error import CacodcarError
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

        attrs_action = set(list(action[self.collection()]))
        attrs_fields = set([i.name for i in fields(self)])

        if not attrs_action <= attrs_fields:
            raise CacodcarError(f'{self}: attributes not in fields')

    @staticmethod
    @abstractmethod
    def collection():
        """reports what collection the component belongs to"""

    @classmethod
    def quantify(cls):
        """reports what quantitative attributes can be given to the component"""
        return nature[cls.collection()]['quantify']

    @classmethod
    def expenses(cls):
        """reports what costs attributes can be given to the component"""
        return nature[cls.collection()]['expenses']

    @classmethod
    def landuse(cls):
        """reports what land attributes can be given to the component"""
        return nature[cls.collection()]['landuse']

    @classmethod
    def resourcebnds(cls):
        """reports what resource attributes can be given to the component"""
        return nature[cls.collection()]['resourcebnds']

    @classmethod
    def resourceexps(cls):
        """reports what resource attributes can be given to the component"""
        return nature[cls.collection()]['resourceexps']

    @classmethod
    def materialuse(cls):
        """reports what material attributes can be given to the component"""
        return nature[cls.collection()]['materialuse']

    @classmethod
    def emitted(cls):
        """reports what emissions attributes that can be given to the component"""
        return nature[cls.collection()]['emitted']

    @classmethod
    def loss(cls):
        """reports what loss attributes that can be given to the component"""
        return nature[cls.collection()]['loss']

    @classmethod
    def inputs(cls):
        """reports what attributes can be given to the component"""
        return (
            cls.emitted()
            + cls.expenses()
            + cls.landuse()
            + cls.loss()
            + cls.materialuse()
            + cls.resourcebnds()
            + cls.resourceexps()
            + cls.quantify()
        )

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

                if attr in self.quantify():
                    setattr(self, attr, self.make_spttmpdict(value))

                if attr in self.expenses():
                    setattr(self, attr, {self._cash: self.make_spttmpdict(value)})

                if attr in self.landuse():
                    setattr(self, attr, {self._land: self.make_spttmpdict(value)})

                if (
                    attr
                    in self.materialuse()
                    + self.loss()
                    + self.emitted()
                    + self.resourcebnds()
                ):
                    setattr(
                        self,
                        attr,
                        {i: self.make_spttmpdict(j) for i, j in value.items()},
                    )

                if attr in self.resourceexps():
                    setattr(
                        self,
                        attr,
                        {
                            i: {self._cash: self.make_spttmpdict(j)}
                            for i, j in value.items()
                        },
                    )

        self._consistent = True


@dataclass
class _Asset(_Defined):
    """Asset Commodity Component"""

    def __post_init__(self):
        _Defined.__post_init__(self)


@dataclass
class _Trade(_Defined):
    """Trade Commodity Component"""

    emission: IsExactInput = field(default=None)

    def __post_init__(self):
        _Defined.__post_init__(self)


@dataclass
class _Impact(_Defined):
    """Impact Component"""

    def __post_init__(self):
        _Defined.__post_init__(self)


@dataclass
class _Operational(_Defined):
    """Operational Component"""

    capacity: IsBoundInput = field(default=None)
    operate: IsBoundInput = field(default=None)
    land: IsExactInput = field(default=None)
    material: IsExactInput = field(default=None)
    capex: IsExactInput = field(default=None)
    opex: IsExactInput = field(default=None)
    emission: IsExactInput = field(default=None)

    def __post_init__(self):
        _Defined.__post_init__(self)


@dataclass
class _Analytical(_Defined):
    """Analytical Component"""

    def __post_init__(self):
        _Defined.__post_init__(self)
