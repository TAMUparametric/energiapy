"""General classes for Components and Model Elements
"""
from dataclasses import dataclass


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


class ClassName:
    """Returns class name
    """

    @classmethod
    def cname(cls) -> str:
        """Returns class name
        """
        return cls.__name__


@dataclass
class Base(Magics, Dunders, ClassName):
    """Basic stuff needed for everything, 
    named after the legendary opening batsman Virender Sehwag
    """
