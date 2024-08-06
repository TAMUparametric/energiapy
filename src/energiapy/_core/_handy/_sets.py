""""collections of sets for collecting declared Model constituents
"""

from dataclasses import dataclass

from src.energiapy import data

from ...funcs.add.component import add_component


@dataclass
class _ElementSets:
    """Sets of Elements associated with Object"""

    def __post_init__(self):
        for i in ['parameters', 'variables', 'constraints', 'ctypes']:
            setattr(self, i, [])

    def params(self):
        """prints parameters of the Object"""
        for i in getattr(self, 'parameters'):
            print(i)

    def vars(self):
        """prints variables of the Object"""
        for i in getattr(self, 'variables'):
            print(i)

    def cons(self):
        """prints constraints of the Object"""
        for i in getattr(self, 'constraints'):
            print(i)


