"""A discretization of the scope 
"""

from dataclasses import dataclass
from ._component import _Component


@dataclass
class _Discr(_Component):
    """A discretization of the scope
    - Scales for Horizon
    - Locations for Network
    """

    def __post_init__(self):
        _Component.__post_init__(self)

    @property
    def parent(self):
        """Parent of the Discretization"""
        return self._parent

    @parent.setter
    def parent(self, disc):
        self._parent = disc

    @property
    def child(self):
        """Child of the Discretization"""
        return self._child

    @child.setter
    def child(self, disc):
        self._child = disc

    @property
    def index(self):
        """Index of the Discretization"""
        return (self.parent.index, self)
