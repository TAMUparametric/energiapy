"""Library of elements"""

from __future__ import annotations

from ..components.commodity.currency import Currency
from ..components.impact.categories import Environ
from ..components.measure.unit import Unit
from ..components.temporal.scales import TemporalScales

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..represent.model import Model


def time_units(model: Model):
    """Time units"""
    model.h = TemporalScales([1, 365, 24, 60, 60], ['y', 'd', 'h', 'min', 's'])


def si_units(model: Model):
    """SI units"""
    # Base units
    model.m = Unit(label='m')  # meter
    model.kg = Unit(label='kg')  # kilogram

    model.km = 1000 * model.m  # kilometer

    # Derived units
    model.kW = 1000 * Unit(label='W')  # kilowatt
    model.MW = 1000 * model.kW  # megawatt
    model.GW = 1000 * model.MW  # gigawatt

    model.J = Unit(label='J')  # joule
    model.kJ = 1000 * model.J  # kilojoule
    model.MJ = 1000 * model.kJ  # megajoule

    model.siunits_set = True


def misc_units(model: Model):
    """Miscellaneous units"""

    if not model.siunits_set:
        si_units(model)

    model.L = 0.001 * Unit(label='m^3')  # liter
    model.gallon = 3.78541 * model.L  # gallon
    model.barrel = 158.987 * model.L  # barrel
    model.mmbtu = 1.055e9 * model.J  # million british thermal unit
    model.ton = 1000 * model.kg  # tonne
    model.miles = 1.60934 * Unit(label='miles')  # miles
    model.PJ = 1e15 * model.J  # petajoule
    model.GJ = 1e9 * model.J  # gigajoule


def env_indicators(model):
    """Load default indicators"""
    model.GWP = Environ(label='Global Warming Potential (kg CO2)')
    model.ODP = Environ(label='Ozone Depletion Potential (CFC-11 eq')
    model.AP = Environ(label='Acidification Potential (kg SO2)')
    model.EP = Environ(label='Eutrophication Potential (kg PO4)')
    model.POCP = Environ(label='Photochemical Ozone Creation Potential (kg C2H4)')
    model.HTP = Environ(label='Human Toxicity Potential (kg 1,4-DCB)')
    model.ETP = Environ(label='Ecotoxicity Potential (kg 1,4-DCB)')
    model.FFDP = Environ(label='Fossil Fuel Depletion Potential (kg oil)')
    model.MRDP = Environ(label='Mineral Resource Depletion Potential (kg resource)')


def currencies(model: Model):
    """Load default currencies

    citation
    --------
    Triennial Central Bank Survey: Foreign Exchange Turnover in April 2022.
    Bank for International Settlements,
    27 Oct. 2022, p. 12. Bank for International Settlements,
    https://www.bis.org/statistics/rpfx22_fx.pdf

    """
    model.USD = Currency(label='U.S. Dollar')
    model.EUR = Currency(label='Euro')
    model.JPY = Currency(label='Japanese Yen')
    model.GBP = Currency(label='Pound Sterling')
    model.CNY = Currency(label='Renminbi')
    model.AUD = Currency(label='Australian Dollar')
    model.CAD = Currency(label='Canadian Dollar')
    model.CHF = Currency(label='Swiss Franc')
    model.HKD = Currency(label='Hong Kong Dollar')
    model.SGD = Currency(label='Singapore Dollar')
    model.SEK = Currency(label='Swedish Krona')
    model.KRW = Currency(label='South Korean Won')
    model.NOK = Currency(label='Norwegian Krone')
    model.NZD = Currency(label='New Zealand Dollar')
    model.INR = Currency(label='Indian Rupee')
    model.MXN = Currency(label='Mexican Peso')
    model.TWD = Currency(label='New Taiwan Dollar')
    model.ZAR = Currency(label='South African Rand')
    model.BRL = Currency(label='Brazilian Real')
    model.DKK = Currency(label='Danish Krone')
    model.PLN = Currency(label='Polish Złoty')
    model.THB = Currency(label='Thai Baht')
    model.ILS = Currency(label='Israeli New Shekel')
    model.IDR = Currency(label='Indonesian Rupiah')
    model.CZK = Currency(label='Czech Koruna')
    model.AED = Currency(label='UAE Dirham')
    model.TRY_ = Currency(label='Turkish Lira')  # TRY is reserved in Python
    model.HUF = Currency(label='Hungarian Forint')
    model.CLP = Currency(label='Chilean Peso')
    model.SAR = Currency(label='Saudi Riyal')
    model.PHP = Currency(label='Philippine Peso')
    model.MYR = Currency(label='Malaysian Ringgit')
    model.COP = Currency(label='Colombian Peso')
    model.RUB = Currency(label='Russian Ruble')
    model.RON = Currency(label='Romanian Leu')
    model.PEN = Currency(label='Peruvian Sol')
