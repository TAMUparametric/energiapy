"""Initial values for the Scenario class
"""

from dataclasses import dataclass, field

from ..._core._handy._dunders import _Dunders
from ...components.analytical.player import Player
from ...components.commodity.cash import Cash
from ...components.commodity.emission import Emission
from ...components.commodity.land import Land
from ...components.scope.horizon import Horizon
from ...components.scope.network import Network

# from ...utils.decorators import once


@dataclass
class _Default(_Dunders):
    """initializations for the Scenario class"""

    default_scope: bool = field(default=False)
    default_players: bool = field(default=False)
    default_emissions: bool = field(default=False)
    default_cash: bool = field(default=False)
    default_land: bool = field(default=False)
    default: bool = field(default=False)

    def _default(self):
        """Set default components"""

        # these are some initializations, which include:
        # Assets - Land and Cash
        # Emissions if default_emissions is True
        # Players if default_players is True (default)
        # Scope Components

        if self.default:
            (
                self.default_players,
                self.default_emissions,
                self.default_cash,
                self.default_land,
                self.default_scope,
            ) = (True for _ in range(5))

        if self.default_scope:
            setattr(self, 'hrz_def', Horizon(label='Default Horizon'))
            setattr(self, 'ntw_def', Network(label='Default Network'))

        if self.default_land:
            setattr(self, 'lnd_def', Land(basis='Acres', label='Land'))

        if self.default_cash:
            setattr(self, 'csh_def', Cash(basis='$', label='Cash'))

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

        if self.default_players or self.default:

            players = [
                ('dm', 'Decision Maker'),
                ('market', 'Commodity Market'),
                ('consumer', 'Demand Consumer'),
                ('earth', 'Planet that absorbs the rest'),
            ]

            for i, j in players:
                setattr(self, i, Player(label=j))
