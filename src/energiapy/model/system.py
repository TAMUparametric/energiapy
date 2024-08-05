from dataclasses import dataclass, field

from .._core._handy._dunders import _Dunders
from .._core._handy._sets import _ComponentSets
from ..funcs.add.component import add_component


@dataclass
class System(_Dunders, _ComponentSets):
    """Collects System Components"""

    name: str = field(default=None)

    def __post_init__(self):
        _ComponentSets.__post_init__(self)

        self.name = f'System|{self.name}|'

        # there are only one each of these

        self.network, self.horizon = None, None

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
