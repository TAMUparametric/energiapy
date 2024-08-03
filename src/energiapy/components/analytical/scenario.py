"""The main object in energiapy. Everything else is defined as a scenario attribute.
"""

from dataclasses import dataclass, field

from ...components.spatial.linkage import Linkage
from ...components.spatial.location import Location
from ...components.spatial.network import Network
from ...components.temporal.horizon import Horizon
from ...funcs.add_to.component import add_component
from ...components.commodity.cash import Cash
from ...components.commodity.emission import Emission
from ...components.commodity.land import Land
# from ...analysis.player import Players
from ..._core._imports._dunders import _Dunders
from ...model.data import Data
from ...model.matrix import Matrix
from ...model.program import Program
from ...model.system import System

# if TYPE_CHECKING:
# from ..types.alias import IsComponent
# from .player import Player


@dataclass
class Scenario(_Dunders):
    """
    A scenario for a considered system. It collects all the components of the model.

    Input:
        name (str, optional): Name. Defaults to 'energia'.
        horizon (Horizon): Planning horizon of the problem, generated post-initialization.
        scales (List[Scale]): List of Scale objects, generated post-initialization.
        resources (List[Resource]): List of Resource objects, generated post-initialization.
        processes (List[Process]): List of Process objects, generated post-initialization.
        locations (List[Location]): List of Location objects, generated post-initialization.
        transports (List[Transit]): List of Transit objects, generated post-initialization.
        linkages (List[Linkage]): List of Linkage objects, generated post-initialization.
        network (Network): Network

    Examples:

        There is not much to this class, it is just a container for the components of the model.

        >>> from energiapy.components import Scenario
        >>> s = Scenario(name='Current')

    """

    name: str = r'\m/>'
    basis_land: str = 'Acres'
    basis_cash: str = '$'
    default_players: bool = field(default=True)
    default_emissions: bool = field(default=True)

    def __post_init__(self):
        self.horizon = None
        self.scales = []
        self.network = Network(name=self.name)

        self.program = Program(name=self.name)
        self.system = System(name=self.name)
        self.matrix = Matrix(name=self.name)
        self.data = Data(name=self.name)

        # if self.default_players:
        #     players = [('dm', 'Decision Maker'), ('market', 'Commodity Market'),
        #                ('consumer', 'Demand Consumer'), ('earth', 'Planet that absorbs the rest')]
        #     for i, j in players:
        #         setattr(self, i, Player(name=i, label=j))

        # assets
        self.land = Land(basis=self.basis_land, label='Land')
        self.cash = Cash(basis=self.basis_cash, label='Cash')

        if getattr(self, 'default_emissions'):
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

    def __setattr__(self, name, value):

        if isinstance(value, Horizon) and not value._named:

            print('asas')
            setattr(value, 'name', name)
            self.horizon, self.scales = value, value.scales
            for i in value.scales:
                setattr(self, i.name, i)

        elif isinstance(value, Network):
            pass

        elif isinstance(value, (Location, Linkage)):
            self.personalize(name, value)
            add_component(
                to=self, list_attr=value.collection, add=value)
            add_component(
                to=self.network, list_attr=value.collection, add=value)

        super().__setattr__(name, value)

    def personalize(self, name, component):
        """Personalize the incoming compoenent 
        """
        setattr(component, 'name', name)
        setattr(component, '_horizon', self.horizon)
        setattr(component, '_network', self.network)
