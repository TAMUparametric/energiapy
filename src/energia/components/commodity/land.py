"""Land"""

from dataclasses import dataclass
from ._commodity import _Commodity
from ...modeling.variables.default import Produce, Trade, Utilize


@dataclass
class Land(_Commodity, Trade, Produce, Utilize):
    """Land used by Operations"""

    def __post_init__(self):
        _Commodity.__post_init__(self)
