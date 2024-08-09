from dataclasses import dataclass, field

from ._component import _Component

from ._consistent import _Consistent


@dataclass
class _DefinedComponent(_Component, _Consistent):
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

    def __setattr__(self, name, value):

        # value = self.make_spttmpdict(value)
        value = self.make_consistent(value=value)
        print(value)

        # args = {'name': name, index = }

        # if isinstance(value, (float, int)) and not isinstance(value, bool):
        #     return Constant(number=value, **args)

        # if isinstance(value, bool):
        #     return M(big=value, **args)

        # if isinstance(value, DataFrame):
        #     return DataSet(data=value, **args)

        # if isinstance(value, tuple):
        #     return Theta(space=value, **args)

        # # if passing a BigM or Th, update
        # if hasattr(value, 'big') or hasattr(value, 'space'):
        #     for i, j in args.items():
        #         setattr(value, i, j)
        #     return value

        super().__setattr__(name, value)

    @property
    def _horizon(self):
        """The Horizon of the Component"""
        return self._system.horizon

    @property
    def _network(self):
        """The Network of the Component"""
        return self._system.network


@dataclass
class _Asset(_DefinedComponent):
    """Asset Component"""

    def __post_init__(self):
        _DefinedComponent.__post_init__(self)


@dataclass
class _Commodity(_DefinedComponent):
    """Commodity Component"""

    def __post_init__(self):
        _DefinedComponent.__post_init__(self)


@dataclass
class _Operational(_DefinedComponent):
    """Operational Component"""

    def __post_init__(self):
        _DefinedComponent.__post_init__(self)


@dataclass
class _Analytical(_DefinedComponent):
    """Analytical Component"""

    def __post_init__(self):
        _DefinedComponent.__post_init__(self)
