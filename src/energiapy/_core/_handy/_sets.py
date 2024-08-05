""""collections of sets for collecting declared Model constituents
"""

from dataclasses import dataclass
from ...funcs.add_to.component import add_component


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


@dataclass
class _ComponentSets:
    """Sets of Components associated with Object"""

    def __post_init__(self):
        # Collections
        plys = ['players']
        cmds = ['resources', 'materials', 'emissions', 'assets']
        opns = ['processes', 'storages', 'transits']
        spts = ['locations', 'linkages']
        temp = ['scales']

        comps = plys + cmds + opns + spts + temp
        for i in comps:
            setattr(self, i, [])

    def add(self, component):
        """Add a Component to System"""
        add_component(self, list_attr=component.collection, add=component)
