
from dataclasses import dataclass, field

from .._core._imports._dunders import _Dunders


@dataclass
class _ScopeComponent(_Dunders):
    """Components which have only one instance in the model
    Horizon and Network 
    """
    name: str = field(default=None)

    def __post_init__(self):
        self.ctypes = []

    @property
    def _named(self):
        if self.name:
            return True
        else:
            return False


@dataclass
class _Component(_ScopeComponent):
    """Common initial attributes of components
    """
    label: str = field(default=None)
    basis: str = field(default=None)
    citation: dict = field(default=None)  # for each attribute make dict
    block: str = field(default=None)
    introduce: str = field(default=None)
    retire: str = field(default=None)

    def __post_init__(self):
        _ScopeComponent.__post_init__(self)

        self._horizon = None
        self._network = None

    def __setattr__(self, name, value):

        if name in ['basis'] and value and self._ready:
            print(name, value, 'yes')

        super().__setattr__(name, value)

    @property
    def _ready(self):
        if self._named and self._horizon and self._network:
            return True
        else:
            return False
