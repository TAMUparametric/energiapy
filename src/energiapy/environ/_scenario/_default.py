"""This has some optional default Components for the Scenario
"""

from dataclasses import dataclass, field

from ...components.analytical.player import Player
from ...components.commodity.cash import Cash
from ...components.commodity.emission import Emission
from ...components.commodity.land import Land
from ...components.scope.spatial.network import Network
from ...components.scope.temporal.horizon import Horizon


@dataclass
class _Default:
    """initializations for the Scenario class

    Such as:
        1. Network with no Locations or Linkages
        2. Horizon with only a root scale, i.e. the planning horizon (ph)
        3. Land with no bounds
        4. Cash with no bounds
        5. Players, viz. Consumer, Decision Maker, Market , Earth
        6. Emissions such as gwp, odp, etc.

    Attributes:
        def_scope (bool): create default Scope (Network, Horizon) Components. Default is False
        def_players (bool): create default (Players) Components. Default is False
        def_emissions (bool): create default (Emission) Components. Default is False
        def_cash (bool): create default (Cash) Components. Default is False
        def_land (bool): create default (Land) Components. Default is False
        default (bool): create default Components of all the above. Default is False
    """

    def_scope: bool = field(default=False)
    def_players: bool = field(default=False)
    def_emissions: bool = field(default=False)
    def_cash: bool = field(default=False)
    def_land: bool = field(default=False)
    default: bool = field(default=False)

    def __post_init__(self):
        if self.default:
            (
                self.def_players,
                self.def_emissions,
                self.def_cash,
                self.def_land,
                self.def_scope,
            ) = (True for _ in range(5))

    def _default(self):
        """Set default components"""

        # these are some initializations, which include:
        # Assets - Land and Cash
        # Emissions if def_emissions is True
        # Players if def_players is True (default)
        # Scope Components

        if self.def_scope:
            setattr(self, 'hrz_def', Horizon(label='Default Horizon'))
            setattr(self, 'ntw_def', Network(label='Default Network'))

        if self.def_land:
            setattr(self, 'lnd_def', Land(basis='Acres', label='Land'))

        if self.def_cash:
            setattr(self, 'csh_def', Cash(basis='$', label='Cash'))

        if self.def_emissions:
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

        if self.def_players or self.default:

            players = [
                ('dm', 'Decision Maker'),
                ('market', 'Commodity Market'),
                ('consumer', 'Demand Consumer'),
                ('earth', 'Planet that absorbs the rest'),
            ]

            for i, j in players:
                setattr(self, i, Player(label=j))
