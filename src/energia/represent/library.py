"""Library of elements"""

from ..components.temporal.period import Period
from ..components.measure.unit import Unit
from ..components.commodity.misc import Currency
from ..components.impact.categories import Environ


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
        self.h = Period(label='Hour')
        self.d = 24 * self.h
        self.y = 365 * self.d

    def load_units(self):
        """Load default units"""
        self.mw = Unit(label='MW')
        self.kg = Unit(label='kg')
        self.ton = 1000 * self.kg

    def load_indicators(self):
        """Load default indicators"""
        self.gwp = Environ(label='Global Warming Potential')
        # self.odp = EnvImp(label='Ozone Depletion Potential')
        self.htp = Environ(label='Human Toxicity Potential')
