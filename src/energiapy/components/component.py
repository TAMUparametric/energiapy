"""These are methods that are common to all Component dataclasses
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from ..funcs.aspect import aspectdicter, aspecter
from ..funcs.component import initializer, namer
from ..funcs.conversion import conversioner
from ..funcs.general import Classer, Collector, Dunders, Magics, Printer

if TYPE_CHECKING:
    from .horizon import Horizon
    from .type.alias import IsComponent, IsValue


class Preparer:
    """names the components from the Scenario attribute
    For example, 
    s = Scenario()
    s.h = Horizon(...)
    s.r = Resource(..)
    then s.r.name = 'r', s.r.horizon = s.h
    """

    def make_named(self, name: str, horizon: Horizon):
        """names and adds horizon to the Resource

        Args:
            name (str): name given as Scenario.name = Resource(...)
            horizon (Horizon): temporal horizon
        """
        namer(component=self, name=name, horizon=horizon)

    def is_ready(self, attr_value: IsValue) -> bool:
        """Checks if attribute is ready to be made into an Aspect

        Args:
            attr_value (IsValue): value assigned to aspect attribute

        Returns:
            bool: True if component is ready and value is assigned
        """
        cndtn_named = hasattr(self, '_named') and getattr(
            self, '_named')
        cndtn_value = attr_value is not None
        if cndtn_named and cndtn_value:
            return True
        else:
            return False


class Initializer:
    """Initializes common attributes of a component
    named, name, horizon, declared_at, ctypes
    """

    def __post_init__(self):
        initializer(component=self)


class Sehwag(Initializer, Collector):
    """Named after the great opening batsman Virender Sehwag
    Initializes and creates collections
    """

    def __post_init__(self):
        Initializer.__post_init__(self)
        Collector.__post_init__(self)


class Aspecter:
    """Updates component attributes to aspects 
    """

    def make_aspect(self, attr_name: str, attr_value: IsValue):
        """Makes Aspect

        Args:
            attr_name (str): name of the attribute
            attr_value (IsValue): value of the attribute
        """
        aspecter(component=self, attr_name=attr_name, attr_value=attr_value)

    def make_aspectdict(self, attr_name: str):
        """Makes AspectDict

        Args:
            attr_name (str): name of the attribute
        """
        aspectdicter(component=self, attr_name=attr_name)


class Component(Sehwag, Dunders, Magics, Preparer, Aspecter, Printer, Classer):
    """Most energiapy components are inherited from this.
    Some like Horizon, TemporalScale, Scenario only take a subset of the methods 
    """


class ProcessChotu:
    """Process specific methods
    """

    def make_conversion(self):
        """Makes Conversion for Process
        """
        conversioner(process=self)

    def __post_init__(self):
        setattr(self, 'materials', [])
