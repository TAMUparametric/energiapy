from dataclasses import dataclass

from .._base._defined import _Impact


@dataclass
class Emission(_Impact):
    """Emission derived from:
    Resource Consume and Discharge
    Material Use
    Operation Capacity
    """

    def __post_init__(self):
        _Impact.__post_init__(self)

    @staticmethod
    def quantify():
        """The quantified data inputs to the component"""
        return []

    @staticmethod
    def expenses():
        """The quantified costs of the component"""
        return []

    @staticmethod
    def collection():
        """The collection in scenario"""
        return 'emissions'
