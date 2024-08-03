
from dataclasses import dataclass, field


@dataclass
class System:
    """Collects system components
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
