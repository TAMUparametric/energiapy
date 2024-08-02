from dataclasses import dataclass, field

from ...components.commodity.cash import Cash
from ...components.commodity.emission import Emission
from ...components.commodity.land import Land
from ...components.spatial.network import Network
# from ...analysis.player import Players
from .common import Dunders, ElmCollect


@dataclass
class ScnInit(Dunders, ElmCollect):
    """These are the initial attributes of a Scenario
    """
    basis_land: str = 'Acres'
    basis_cash: str = '$'
    default_players: bool = field(default=True)
    default_emissions: bool = field(default=True)

    def __post_init__(self):
        ElmCollect.__post_init__(self)
        self.program = Program()
        self.design = Design()
        self.matrix = Matrix()
        self.data = Data()
        # if self.default_players:
        #     players = [('dm', 'Decision Maker'), ('market', 'Commodity Market'),
        #                ('consumer', 'Demand Consumer'), ('earth', 'Planet that absorbs the rest')]
        #     for i, j in players:
        #         setattr(self, i, Player(name=i, label=j))

        # collected components
        plys = ['players']
        cmds = ['resources', 'materials', 'emissions', 'assets']
        opns = ['processes', 'storages', 'transits']
        spts = ['locations', 'linkages']

        comps = plys + cmds + opns + spts
        for i in comps:
            setattr(self, f'{i}', [])

        # set components
        self.horizon, self.scales = None, []

        self.network = Network(label='Network')

        # assets
        self.land = Land(basis=self.basis_land, label='Land')
        self.cash = Cash(basis=self.basis_cash, label='Cash')

        if self.default_emissions:
            emissions = [
                ('gwp', 'kg CO2 eq.', 'Global Warming Potential'),
                ('ap', 'mol eq', 'Acidification Potential'),
                ('epm', 'kg P eq', 'Eutrophication Potential (Marine)'),
                ('epf', 'kg P eq', 'Eutrophication Potential (Freshwater)'),
                ('ept', 'kg P eq', 'Eutrophication Potential (Terrestrial)'),
                ('pocp', 'kg NMVOC eq', 'Photochemical Ozone Creation Potential'),
                ('odp', 'kg CFC 11 eq', 'Ozone Depletion Potential'),
                ('adpmn', 'kg Sb eq', 'Abiotic Depletion Potential (Mineral)'),
                ('adpmt', 'kg Sb eq', 'Abiotic Depletion Potential (Metal)'),
                ('adpf', 'MJ', 'Abiotic Depletion Potential (Fossil)'),
                ('wdp', 'm^3', 'Water Deprivation Potential')
            ]
            for i, j, k in emissions:
                setattr(self, i, Emission(basis=j, label=k))
