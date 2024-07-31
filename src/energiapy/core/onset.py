"""Element collects for Model Units and Components 
"""
from __future__ import annotations

from dataclasses import dataclass, fields
from typing import TYPE_CHECKING

from ...components.commodity.cash import Cash
from ...components.commodity.emission import Emission
from ...components.commodity.land import Land

if TYPE_CHECKING:
    from ..components.temporal.horizon import Horizon
    from ..type.alias import IsInput


@dataclass
class ScnInit:
    """These are the initial attributes of a Scenario
    """
    basis_land: str = 'Acres'
    basis_cash: str = '$'

    def __post_init__(self):
        setattr(self, 'land', Land(basis=self.basis_land, label='Land'))
        setattr(self, 'cash', Cash(basis=self.basis_cash, label='Cash'))
        # Emission
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

        self.horizon, self.network = None, None

        # create empty attributes to collect components
        cmds = ['resource', 'material', 'emission']
        opns = ['process', 'storage', 'transit']
        spts = ['location', 'linkage']
        comps = cmds + opns + spts
        for i in comps:
            setattr(self, f'{i}_all', [])


@dataclass
class CmpInit:
    """Common initial attributes of a component
    named, name, horizon, declared_at, ctypes
    """

    def __post_init__(self):
        self._named = None
        self.name = None
        self.horizon = None
        self.declared_at = self
        self.ctypes = []

    def make_named(self, name: str, horizon: Horizon):
        """names and adds horizon to the Resource

        Args:
            name (str): name given as Scenario.name = Resource(...)
            horizon (Horizon): temporal horizon
        """

        setattr(self, 'name', name)
        setattr(self, 'horizon', horizon)
        setattr(self, '_named', True)

        for i in fields(self):
            attr = i.name.lower()
            if hasattr(self, attr) and getattr(self, attr) is not None:
                setattr(self, attr, getattr(self, attr))

    def is_ready(self, attr_value: IsInput) -> bool:
        """Checks if attribute is ready to be made into an Aspect

        Args:
            attr_value (IsInput): value assigned to aspect attribute

        Returns:
            bool: True if component is ready and value is assigned
        """
        cndtn_named = hasattr(self, '_named') and getattr(
            self, '_named')
        cndtn_value = attr_value is not None
        if cndtn_named and cndtn_value:
            return True
        else:
            return False


@dataclass
class EmtCol:
    """Lists for collecting modeling elements
    parameters, variables, constraints
    """

    def __post_init__(self):
        self.parameters = []
        self.variables = []
        self.constraints = []

    def params(self):
        """prints parameters of the Component
        """
        for i in self.parameters:
            print(i)

    def vars(self):
        """prints variables of the Component
        """
        for i in self.variables:
            print(i)

    def cons(self):
        """prints constraints of the Component
        """
        for i in self.constraints:
            print(i)
