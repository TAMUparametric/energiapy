"""Emission"""

from dataclasses import dataclass

from ._commodity import _Commodity
from ...modeling.variables.default import Free, Produce, Trade


@dataclass
class Emission(_Commodity, Free, Produce, Trade):
    """Emission"""

    def __post_init__(self):
        _Commodity.__post_init__(self)
