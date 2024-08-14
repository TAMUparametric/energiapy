from dataclasses import dataclass

from .._base._component import _Component


@dataclass
class _Spatial(_Component):
    """Spatial Component"""

    def __post_init__(self):
        _Component.__post_init__(self)
