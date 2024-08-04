
from dataclasses import dataclass, field

from .._core._handy._dunders import _Dunders
from ..funcs.add_to.component import add_component


@dataclass
class System(_Dunders):
    """Collects System Components
    """
    name: str = field(default=None)

    def __post_init__(self):

        self.name = f'System|{self.name}|'

        # set components
        plys = ['players']
        cmds = ['resources', 'materials', 'emissions', 'assets']
        opns = ['processes', 'storages', 'transits']
        spts = ['locations', 'linkages']
        temp = ['scales']

        comps = plys + cmds + opns + spts + temp
        for i in comps:
            setattr(self, f'{i}', [])

        # there are only one each of these
        self.network, self.horizon = None, None

    def add(self, component):
        """Add a Component to System
        """
        add_component(self, list_attr=component.collection, add=component)
