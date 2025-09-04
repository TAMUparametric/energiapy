"""Impact Indicator Categories"""

from dataclasses import dataclass

from ...modeling.variables.default import EcoImp, EnvImp, SocImp
from .indicator import Indicator


@dataclass
class Environ(Indicator, EnvImp):
    """Environmental Impact"""


@dataclass
class Social(Indicator, SocImp):
    """Soc Impact"""


@dataclass
class Economic(Indicator,EcoImp):
    """Economic impact"""



