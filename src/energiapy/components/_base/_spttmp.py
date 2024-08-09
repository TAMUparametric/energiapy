from dataclasses import dataclass

from ._component import _Component


@dataclass
class _Scope(_Component):
    """Components which have only one instance in the model
    Horizon and Network are the only scope components
    """

    def __post_init__(self):
        _Component.__post_init__(self)


@dataclass
class _Temporal(_Component):
    """Temporal Component
    Basically the Scale which is derived from Horizon
    """

    def __post_init__(self):
        _Component.__post_init__(self)


@dataclass
class _Spatial(_Component):
    """Spatial Component"""

    def __post_init__(self):
        _Component.__post_init__(self)
