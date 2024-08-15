
from dataclasses import dataclass

from .._base._component import _Component


@dataclass
class _Temporal(_Component):
    """Temporal Component
    Basically the Scale which is derived from Horizon
    """

    def __post_init__(self):
        _Component.__post_init__(self)
