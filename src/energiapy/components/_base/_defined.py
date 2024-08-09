"""There are user defined components
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from pandas import DataFrame

from ...data.constant import Constant
from ...data.dataset import DataSet
from ...data.m import M
from ...data.theta import Theta
from ._component import _Component
from ._consistent import _Consistent


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

    @staticmethod
    @abstractmethod
    def quantify():
        """reports data inputs that quantify aspects of the component"""

    @staticmethod
    @abstractmethod
    def expenses():
        """reports what costs data can be given to the component"""

    @staticmethod
    @abstractmethod
    def collection():
        """reports what collection the component belongs to"""

    @classmethod
    def inputs(cls):
        """reports what data inputs the component"""
        return cls.quantify() + cls.expenses()

    @property
    def _horizon(self):
        """The Horizon of the Component"""
        return self._system.horizon

    @property
    def _network(self):
        """The Network of the Component"""
        return self._system.network

    def make_consistent(self):
        """Makes the data inputs consistent IsSptTmpDict"""
        for value in self.inputs():

            #     if isinstance(value, (float, int)) and not isinstance(value, bool):
            #         return Constant(constant=value, **args)
            #     if isinstance(value, bool):
            #         return M(big=value, **args)

            #     if isinstance(value, DataFrame):
            #         return DataSet(data=value, **args)

            #     if isinstance(value, tuple):
            #         return Theta(space=value, **args)

            #     # if passing a BigM or Th, update
            #     if hasattr(value, 'big') or hasattr(value, 'space'):
            #         for i, j in args.items():
            #             setattr(value, i, j)
            #         return value

            setattr(self, value, self.make_spttmpdict(getattr(self, value)))
        self._consistent = True


@dataclass
class _Asset(_Defined):
    """Asset Component"""

    def __post_init__(self):
        _Defined.__post_init__(self)


@dataclass
class _Impact(_Defined):
    """Impact Component"""

    def __post_init__(self):
        _Defined.__post_init__(self)


@dataclass
class _Commodity(_Defined):
    """Commodity Component"""

    def __post_init__(self):
        _Defined.__post_init__(self)


@dataclass
class _Operational(_Defined):
    """Operational Component"""

    def __post_init__(self):
        _Defined.__post_init__(self)


@dataclass
class _Analytical(_Defined):
    """Analytical Component"""

    def __post_init__(self):
        _Defined.__post_init__(self)
