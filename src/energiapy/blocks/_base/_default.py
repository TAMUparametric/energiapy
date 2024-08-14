"""Initial values for the Scenario class
"""

from dataclasses import dataclass, field

from ..._core._handy._dunders import _Dunders
from ...components.analytical.player import Player
from ...components.commodity.asset.cash import Cash
from ...components.commodity.asset.land import Land
from ...components.impact.emission import Emission
from ...components.scope.horizon import Horizon
from ...components.scope.network import Network
from ...funcs.utils.decorators import once


@dataclass
class _Default(_Dunders):
    """initializations for the Scenario class"""

    default_players: bool = field(default=True)
    default_emissions: bool = field(default=True)
    default_cash: bool = field(default=True)
    default_land: bool = field(default=True)
    default_all: bool = field(default=False)

    @once
    def _default(self):
        """Set default components"""

        # these are some initializations, which include:
        # Assets - Land and Cash
        # Emissions if default_emissions is True
        # Players if default_players is True (default)
        # Scope Components

        setattr(self, 'h', Horizon(label='Default Horizon'))

        setattr(self, 'n', Network(label='Default Network'))

        if self.default_land or self.default_all:
            setattr(self, 'l', Land(basis='Acres', label='Land'))

        if self.default_cash or self.default_all:
            setattr(self, 'c', Cash(basis='$', label='Cash'))

        if self.default_emissions or self.default_all:
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

            for i, j, k in emissions or self.default_all:
                setattr(self, i, Emission(basis=j, label=k))

        if self.default_players or self.default_all:

            players = [
                ('dm', 'Decision Maker'),
                ('market', 'Commodity Market'),
                ('consumer', 'Demand Consumer'),
                ('earth', 'Planet that absorbs the rest'),
            ]

            for i, j in players:
                setattr(self, i, Player(label=j))
