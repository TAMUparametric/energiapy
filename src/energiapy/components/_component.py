from dataclasses import dataclass, field

from .._core._handy._dunders import _Dunders
from ..funcs.add.component import add_component


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

    def add(self, component):
        """Add a Component to Spatial Component"""
        add_component(self, list_attr=component.collection, add=component)


@dataclass
class _Component(_Dunders):
    """Common initial attributes of components"""

    label: str = field(default=None)
    basis: str = field(default='unit')
    citation: dict = field(default=None)  # for each attribute make dict
    block: str = field(default=None)
    introduce: str = field(default=None)
    retire: str = field(default=None)

    def __post_init__(self):
        self._horizon = None
        self._network = None

    def __setattr__(self, name, value):

        super().__setattr__(name, value)

    @property
    def _named(self):
        """The component has been named"""
        if getattr(self, 'name', False):
            return True

        else:
            return False

    @property
    def _is_scoped(self):
        """The scope of the scenario has been conveyed to the Component"""
        if self._named and self._horizon and self._network:
            return True
        else:
            return False

    def add(self, component):
        """Add a Component to Spatial Component"""
        add_component(self, list_attr=component.collection, add=component)

    def personalize(self, name, horizon, network):
        """Personalize the compoenent
        give it a name (public), _horizon and _network
        """
        setattr(self, 'name', name)
        setattr(self, '_horizon', horizon)
        setattr(self, '_network', network)
