"""Initial values for the Scenario class
"""

from dataclasses import dataclass, field

from .._core._handy._dunders import _Dunders
from .._core._handy._sets import _ComponentSets
from ..components.analytical.player import Player
from ..components.commodity.cash import Cash
from ..components.commodity.emission import Emission
from ..components.commodity.land import Land
from ..components.spatial.network import Network
from ..components.temporal.horizon import Horizon
from ..funcs.utils.decorators import once
from .data import Data
from .matrix import Matrix
from .program import Program
from .system import System


@dataclass
class _Scenario(_Dunders):
    """initializations for the Scenario class"""

    name: str = field(default=r'\m/>')
    basis_land: str = 'Acres'
    basis_cash: str = '$'
    default_players: bool = field(default=True)
    default_emissions: bool = field(default=True)

    def __post_init__(self):
        _ComponentSets.__post_init__(self)

        self._is_initd = False

        # Declare Model
        self.system = System(name=self.name)
        self.program = Program(name=self.name)
        self.data = Data(name=self.name)
        self.matrix = Matrix(name=self.name)

        # Scope Components
        self.horizon = Horizon(name='horizon')
        self.scales = []
        self.network = Network(name='network')

    @once
    def _initialize(self):
        """Set default components"""

        setattr(self, 'land', Land(basis=self.basis_land, label='Land'))
        setattr(self, 'cash', Cash(basis=self.basis_cash, label='Cash'))

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
                ('wdp', 'm^3', 'Water Deprivation Potential'),
            ]

            for i, j, k in emissions:
                setattr(self, i, Emission(basis=j, label=k))

        if self.default_players:

            players = [
                ('dm', 'Decision Maker'),
                ('market', 'Commodity Market'),
                ('consumer', 'Demand Consumer'),
                ('earth', 'Planet that absorbs the rest'),
            ]

            for i, j in players:
                setattr(self, i, Player(label=j))

        self._is_initd = True
