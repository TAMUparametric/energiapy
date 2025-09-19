"""Library of elements"""

from ..components.commodity.misc import Currency
from ..components.impact.categories import Environ
from ..components.measure.unit import Unit
from ..components.temporal.periods import Periods


class Library:

    def library(
        self,
        periods: bool = False,
        units: bool = False,
        currencies: bool = False,
        indicators: bool = False,
    ):
        """Initialize the library"""

        if periods:
            self.load_periods()
        if units:
            self.load_units()
        if currencies:
            self.load_currencies()
        if indicators:
            self.load_indicators()

    def load_currencies(self):
        """Load default currencies"""
        self.usd = Currency(label='USD')

    def load_periods(self):  # , what: list[str] = ['h', 'd', 'y']
        """Load default periods"""
        self.h = Periods(label='Hour')
        self.d = 24 * self.h
        self.y = 365 * self.d

    def load_units(self):
        """Load default units"""
        self.MW = Unit(label='MW')
        self.kg = Unit(label='kg')
        self.ton = 1000 * self.kg
        self.miles = Unit(label='Miles')

    def load_indicators(self):
        """Load default indicators"""
        self.GWP = Environ(label='Global Warming Potential')
        # self.odp = EnvImp(label='Ozone Depletion Potential')
        self.HTP = Environ(label='Human Toxicity Potential')
