"""Helper functions for energiapy components and Model Units
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..components.type.alias import IsComponent


def collector(component: IsComponent):
    """creates lists for collecting modeling units  
    """
    for i in ['parameters', 'variables', 'constraints']:
        setattr(component, i, [])


def printer(component, print_collection):
    """print parameters, variables, constraints

    Args:
        component: energiapy components 
        print_collection (str): 'parameters', 'variables', 'constraints'
    """
    for i in getattr(component, print_collection):
        print(i)


class Magics:
    """Magic functions
    """

    def __lt__(self, other):
        return getattr(self, 'name') < other.name

    def __gt__(self, other):
        return getattr(self, 'name') > other.name


class Dunders:
    """The usual dunder methods for a Component
    """

    def __repr__(self):
        return str(getattr(self, 'name'))

    def __eq__(self, other):
        return getattr(self, 'name') == other.name

    def __hash__(self):
        return hash(getattr(self, 'name'))

    @classmethod
    def __init_subclass__(cls):
        cls.__hash__ = Dunders.__hash__
        cls.__eq__ = Dunders.__eq__
        cls.__repr__ = Dunders.__repr__


class Collector:
    """creates lists for collecting modeling units
    parameters, variables, constraints
    """

    def __post_init__(self):
        collector(component=self)


class Printer:
    """Prints model parameters, variables and constraints
    """

    def params(self):
        """prints parameters of the Component
        """
        printer(component=self, print_collection='parameters')

    def vars(self):
        """prints variables of the Component
        """
        printer(component=self, print_collection='variables')

    def cons(self):
        """prints constraints of the Component
        """
        printer(component=self, print_collection='constraints')


class Classer:
    """Returns class name
    """

    @classmethod
    def cname(cls) -> str:
        """Returns class name
        """
        return cls.__name__
