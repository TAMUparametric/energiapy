"""Hashing Base Class"""

class _Hash:

    def __str__(self):
        return getattr(self, 'name')

    def __repr__(self):
        return getattr(self, 'name')

    def __hash__(self):
        return hash(getattr(self, 'name'))

    def __init_subclass__(cls):
        cls.__repr__ = _Hash.__repr__
        cls.__hash__ = _Hash.__hash__
