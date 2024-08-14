from dataclasses import dataclass

from .._base._component import _Component


@dataclass
class _Scope(_Component):
    """Components which have only one instance in the model
    Horizon and Network are the only scope components
    """

    def __post_init__(self):
        _Component.__post_init__(self)

    @staticmethod
    def collection():
        """The collection in scenario"""
        return 'scopes'
