"""General classes for Components and Model Elements
"""


class _Reprs:
    """The usual dunder methods for a Component
    """

    def __repr__(self):
        return str(getattr(self, 'name'))

    def __eq__(self, other):
        return getattr(self, 'name') == other.name

    def __hash__(self):
        return hash(getattr(self, 'name'))

    def __init_subclass__(cls):
        cls.__repr__ = _Reprs.__repr__
        cls.__eq__ = _Reprs.__eq__
        cls.__hash__ = _Reprs.__hash__


class _Magics:
    """Magic functions
    """

    def __lt__(self, other):
        return getattr(self, 'name') < other.name

    def __gt__(self, other):
        return getattr(self, 'name') > other.name


class _Dunders(_Reprs, _Magics):
    """Dunders for a Component
    """
