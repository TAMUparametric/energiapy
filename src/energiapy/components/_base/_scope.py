"""Scopes define the spatiotemporal boundaris of the System
"""

from dataclasses import dataclass

from ._component import _Component


@dataclass
class _Scope(_Component):
    """These define the spatiotemporal boundaries of the System
    Components which have only one instance in the model
    Horizon and Network are the only scope components
    """

    def __post_init__(self):
        _Component.__post_init__(self)
